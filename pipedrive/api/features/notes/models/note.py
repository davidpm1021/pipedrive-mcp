from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Note(BaseModel):
    """Note entity model with Pydantic validation.

    Notes attach to one or more Pipedrive entities (deal, person, org, lead).
    The Pipedrive v1 API requires at least one entity link on creation.
    """

    content: str
    deal_id: Optional[int] = None
    person_id: Optional[int] = None
    org_id: Optional[int] = None
    lead_id: Optional[str] = None  # Lead IDs are UUIDs
    user_id: Optional[int] = None
    pinned_to_deal_flag: Optional[bool] = None
    pinned_to_person_flag: Optional[bool] = None
    pinned_to_organization_flag: Optional[bool] = None
    pinned_to_lead_flag: Optional[bool] = None
    add_time: Optional[str] = None
    id: Optional[int] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Note content cannot be empty")
        return v

    @field_validator("deal_id", "person_id", "org_id", "user_id", "id")
    @classmethod
    def validate_positive_id(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("ID fields must be positive integers if provided")
        return v

    def to_create_payload(self) -> Dict[str, Any]:
        """Build the JSON payload for POST /notes (excludes id and add_time)."""
        return {
            k: v
            for k, v in self.model_dump().items()
            if v is not None and k not in ("id", "add_time")
        }

    def to_update_payload(self) -> Dict[str, Any]:
        """Build the JSON payload for PUT /notes/{id} (excludes id and add_time)."""
        return self.to_create_payload()
