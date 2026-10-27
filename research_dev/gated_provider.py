"""Opt-in public pilot provider wrapper: enforce custody BEFORE each model call.

Development only. Caller must create durable commitments before constructing this
wrapper. A local HMAC does not establish independent external time custody.
"""
from cohervia_pilot.protocol import catalog
from persistent_custody import PersistentCustody, digest

class CustodyGatedProvider:
    def __init__(self, provider, custody_path, coordinator_secret, run_id, receipts, probabilities):
        self.provider = provider
        self.model = provider.model
        self.kind = provider.kind
        self.run_id = run_id
        self.custody_path = custody_path
        self.coordinator_secret = coordinator_secret
        self.receipts = receipts
        self.probabilities = probabilities
        self.tasks = catalog()
        self.index = 0
        expected = {t["id"] for t in self.tasks}
        if type(receipts) is not dict or type(probabilities) is not dict or set(receipts) != expected or set(probabilities) != expected:
            raise ValueError("exact public task commitments required")

    def complete(self, *, instructions, prompt):
        if self.index >= len(self.tasks):
            raise ValueError("pilot call limit exceeded")
        task = self.tasks[self.index]
        if prompt != task["prompt"]:
            raise ValueError("task prompt/order mismatch")
        trial_id = self.run_id + ":" + task["id"]
        prediction = {"trial_id": trial_id, "task_hash": digest(task),
                      "model": self.model, "probability": self.probabilities[task["id"]]}
        # The transaction commits consumption BEFORE provider.complete is invoked.
        # A failed provider call still consumes its receipt, preventing retry/replay.
        with PersistentCustody(self.custody_path, self.coordinator_secret) as custody:
            custody.authorize(prediction, self.receipts[task["id"]])
        self.index += 1
        return self.provider.complete(instructions=instructions, prompt=prompt)

    def close(self):
        return self.provider.close()
