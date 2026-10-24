"""Base classes for every contract model.

All contract models are strict (no type coercion) and reject unknown fields. Records that must
never change after creation use FrozenContractModel. No business rules live here or in any
contract: weights, thresholds and wording come from playbooks, templates and settings.
"""

from pydantic import BaseModel, ConfigDict


class ContractModel(BaseModel):
    """Strict base for mutable contract models (for example a term before it is confirmed)."""

    model_config = ConfigDict(strict=True, extra="forbid", validate_assignment=True)


class FrozenContractModel(ContractModel):
    """Strict, immutable base. Change a record by creating a new one (model_copy with update)."""

    model_config = ConfigDict(frozen=True)


def requirements(*ids: str) -> ConfigDict:
    """Record the requirement IDs a model serves; they appear in the exported JSON Schema."""
    return ConfigDict(json_schema_extra={"requirements": list(ids)})
