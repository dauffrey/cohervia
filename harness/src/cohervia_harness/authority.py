from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ProtectedResource(StrEnum):
    EVALUATOR = "evaluator"
    OBSERVER = "observer"
    STOP_CONTROLLER = "stop_controller"
    AUDIT_LOG = "audit_log"
    PERMISSIONS = "permissions"
    HOLDOUT_MANIFESTS = "holdout_manifests"


@dataclass(frozen=True, slots=True)
class AuthorityBoundary:
    """External authority policy.

    Acting agents are never authorized to mutate protected resources.
    """

    owner_principal: str = "external_controller"

    def may_mutate(self, *, actor: str, resource: ProtectedResource) -> bool:
        return actor == self.owner_principal

    def require_mutation_authority(
        self, *, actor: str, resource: ProtectedResource
    ) -> None:
        if not self.may_mutate(actor=actor, resource=resource):
            raise PermissionError(
                f"{actor!r} is not authorized to mutate protected resource "
                f"{resource.value!r}"
            )
