import unittest

from cohervia_harness.authority import AuthorityBoundary, ProtectedResource


class AuthorityTests(unittest.TestCase):
    def test_agent_cannot_mutate_protected_resources(self):
        boundary = AuthorityBoundary()
        for resource in ProtectedResource:
            with self.assertRaises(PermissionError):
                boundary.require_mutation_authority(actor="acting_agent", resource=resource)

    def test_external_controller_can_mutate_protected_resources(self):
        boundary = AuthorityBoundary()
        for resource in ProtectedResource:
            boundary.require_mutation_authority(
                actor="external_controller", resource=resource
            )


if __name__ == "__main__":
    unittest.main()
