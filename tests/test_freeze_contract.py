import unittest
from pathlib import Path

from cohervia_harness.freeze import matrix_freeze_requirements, verify_freeze_contract


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "experiments" / "COH-EXP-0001" / "config" / "MATRIX.yaml"
MANIFEST = (
    ROOT / "experiments" / "COH-EXP-0001" / "ARTIFACT_MANIFEST.template.json"
)


class FreezeContractTests(unittest.TestCase):
    def test_all_matrix_requirements_map_to_manifest(self):
        requirements = matrix_freeze_requirements(MATRIX)
        self.assertEqual(len(requirements), 42)
        self.assertEqual(verify_freeze_contract(
            matrix_path=MATRIX,
            manifest_path=MANIFEST,
        ), ())


if __name__ == "__main__":
    unittest.main()
