"""RFC 3161 timestamp authority transport and cryptographic verification.

This adapter uses an independently operated TSA endpoint and a pinned CA file.
It does not supply an endpoint, trust root, credentials, or automatic live calls.
The external witness protocol's 'signature' field carries the base64 DER
TimeStampResp; 'observed_at' is extracted from its signed TSTInfo.
"""
import base64
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from external_witness import verify_witness
from persistent_custody import canonical, digest

def _openssl(*args, input_bytes=None):
    result = subprocess.run(["openssl", *args], input=input_bytes, capture_output=True, check=False, timeout=30)
    if result.returncode:
        raise ValueError("RFC3161 cryptographic validation failed")
    return result.stdout

def _time_from_response(response):
    output = _openssl("ts", "-reply", "-text", input_bytes=response).decode("utf-8")
    match = re.search(r"^Time stamp:\s*(.+)$", output, re.MULTILINE)
    if not match:
        raise ValueError("missing signed TSA generation time")
    from datetime import datetime, timezone
    try:
        moment = datetime.strptime(match.group(1).strip(), "%b %d %H:%M:%S %Y GMT").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("unrecognized TSA generation time") from exc
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")

class RFC3161Witness:
    def __init__(self, url, ca_file, witness_id="rfc3161-tsa", *, timeout=15):
        if not isinstance(url, str) or not url.startswith("https://"):
            raise ValueError("HTTPS TSA endpoint required")
        if not Path(ca_file).is_file():
            raise ValueError("pinned TSA trust anchor required")
        self.url, self.ca_file, self.witness_id, self.timeout = url, str(ca_file), witness_id, timeout

    def _verify_der(self, response, commitment):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "response.tsr").write_bytes(response)
            (path / "commitment.json").write_bytes(canonical(commitment))
            _openssl("ts", "-verify", "-in", str(path / "response.tsr"),
                     "-data", str(path / "commitment.json"), "-CAfile", self.ca_file)
        return True

    def submit(self, commitment):
        raw = canonical(commitment)
        request = _openssl("ts", "-query", "-data", "-", "-sha256", "-cert", input_bytes=raw)
        http = Request(self.url, data=request, headers={"Content-Type": "application/timestamp-query",
                                                         "Accept": "application/timestamp-reply"}, method="POST")
        with urlopen(http, timeout=self.timeout) as reply:
            if reply.headers.get_content_type() != "application/timestamp-reply":
                raise ValueError("unexpected TSA response type")
            response = reply.read(1024 * 1024 + 1)
        if not response or len(response) > 1024 * 1024:
            raise ValueError("invalid TSA response size")
        self._verify_der(response, commitment)
        return {"version": "witness/0.1", "witness_id": self.witness_id,
                "commitment_sha256": digest(commitment), "observed_at": _time_from_response(response),
                "signature": base64.b64encode(response).decode("ascii")}

    def verify(self, receipt, commitment):
        verify_witness(receipt, commitment, lambda _: True, expected_witness_id=self.witness_id)
        try:
            response = base64.b64decode(receipt["signature"], validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ValueError("invalid DER encoding") from exc
        self._verify_der(response, commitment)
        if receipt["observed_at"] != _time_from_response(response):
            raise ValueError("timestamp not bound to signed TSA response")
        return True
