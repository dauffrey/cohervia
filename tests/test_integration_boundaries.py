"""Cross-package boundary regressions; only public checked-in files are read."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class IntegrationBoundaryTests(unittest.TestCase):
    def test_mainline_scientist_and_evidence_policy_bytes_preserved(self):
        manifest=json.loads((ROOT/'docs/implementation/RECONCILIATION_BASELINE.json').read_text())
        self.assertEqual(manifest['baseline_commit'],'fc139abfbc92f0d7ef30dfb6bb032402c8e05456')
        for relative, expected in manifest['protected_blobs'].items():
            with self.subTest(path=relative):
                data=(ROOT/relative).read_bytes()
                digest=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                self.assertEqual(digest,expected)
        # No unreviewed additions to the Scientist runtime/package surface.
        expected={p for p in manifest['protected_blobs'] if p.startswith('scientist/src/')}
        actual={str(p.relative_to(ROOT)) for p in (ROOT/'scientist/src').rglob('*.py')}
        self.assertEqual(actual,expected)

    def test_no_execution_authority_and_manifest_is_still_unfrozen(self):
        authority=json.loads((ROOT/'scientist/config/authority.json').read_text())['permissions']
        self.assertTrue(authority['read_repository'])
        self.assertTrue(all(v is False for k,v in authority.items() if k!='read_repository'))
        manifest=json.loads((ROOT/'experiments/COH-EXP-0001/ARTIFACT_MANIFEST.template.json').read_text())
        self.assertEqual(manifest['status'],'template_not_executed')
        self.assertTrue(all(v is None for k,v in manifest.items() if k not in ('experiment_id','status','notes')))

    def test_relative_markdown_links_resolve(self):
        for p in ROOT.rglob('*.md'):
            if '.git' in p.parts or '__pycache__' in p.parts:
                continue
            for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)',p.read_text()):
                if ':' in target or target.startswith('#'):
                    continue
                target=target.split('#')[0]
                if target:
                    with self.subTest(file=str(p.relative_to(ROOT)),target=target):
                        self.assertTrue((p.parent/target).exists())
