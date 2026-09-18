import json
from typing import Any, Dict, List, Optional, Tuple

from log_config import logger
from pipedrive.api.base_client import BaseClient


class NoteClient:
    """Client for Pipedrive Note API endpoints (v1)."""

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    async def create_note(
        self,
        content: str,
        deal_id: Optional[int] = None,
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        lead_id: Optional[str] = None,
        user_id: Optional[int] = None,
        pinned_to_deal_flag: Optional[bool] = None,
        pinned_to_person_flag: Optional[bool] = None,
        pinned_to_organization_flag: Optional[bool] = None,
        pinned_to_lead_flag: Optional[bool] = None,
        add_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a note in Pipedrive.

        Pipedrive v1 requires at least one of deal_id/person_id/org_id/lead_id.
        """
        logger.info("NoteClient: creating note")

        if not content or not content.strip():
            raise ValueError("Note content cannot be empty")
        if all(v is None for v in (deal_id, person_id, org_id, lead_id)):
            raise ValueError(
                "At least one of deal_id, person_id, org_id, or lead_id must be provided"
            )

        payload: Dict[str, Any] = {"content": content}
        for k, v in (
            ("deal_id", deal_id),
            ("person_id", person_id),
            ("org_id", org_id),
            ("lead_id", lead_id),
            ("user_id", user_id),
            ("pinned_to_deal_flag", pinned_to_deal_flag),
            ("pinned_to_person_flag", pinned_to_person_flag),
            ("pinned_to_organization_flag", pinned_to_organization_flag),
            ("pinned_to_lead_flag", pinned_to_lead_flag),
            ("add_time", add_time),
        ):
            if v is not None:
                payload[k] = v

        logger.debug(f"NoteClient: create_note payload: {json.dumps(payload)}")
        response = await self.base_client.request(
            "POST", "/notes", json_payload=payload, version="v1"
        )
        return response.get("data", {})

    async def get_note(self, note_id: int) -> Dict[str, Any]:
        """Get a single note by ID."""
        logger.info(f"NoteClient: getting note {note_id}")
        if note_id <= 0:
            raise ValueError(f"Invalid note_id: {note_id}. Must be a positive integer.")

        response = await self.base_client.request(
            "GET", f"/notes/{note_id}", version="v1"
        )
        return response.get("data", {})

    async def update_note(
        self,
        note_id: int,
        content: Optional[str] = None,
        deal_id: Optional[int] = None,
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        lead_id: Optional[str] = None,
        user_id: Optional[int] = None,
        pinned_to_deal_flag: Optional[bool] = None,
        pinned_to_person_flag: Optional[bool] = None,
        pinned_to_organization_flag: Optional[bool] = None,
        pinned_to_lead_flag: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update an existing note."""
        logger.info(f"NoteClient: updating note {note_id}")
        if note_id <= 0:
            raise ValueError(f"Invalid note_id: {note_id}. Must be a positive integer.")

        payload: Dict[str, Any] = {}
        for k, v in (
            ("content", content),
            ("deal_id", deal_id),
            ("person_id", person_id),
            ("org_id", org_id),
            ("lead_id", lead_id),
            ("user_id", user_id),
            ("pinned_to_deal_flag", pinned_to_deal_flag),
            ("pinned_to_person_flag", pinned_to_person_flag),
            ("pinned_to_organization_flag", pinned_to_organization_flag),
            ("pinned_to_lead_flag", pinned_to_lead_flag),
        ):
            if v is not None:
                payload[k] = v

        if not payload:
            raise ValueError("At least one field must be provided for updating a note.")

        logger.debug(f"NoteClient: update_note payload: {json.dumps(payload)}")
        response = await self.base_client.request(
            "PUT", f"/notes/{note_id}", json_payload=payload, version="v1"
        )
        return response.get("data", {})

    async def list_notes(
        self,
        limit: int = 100,
        start: int = 0,
        deal_id: Optional[int] = None,
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        lead_id: Optional[str] = None,
        user_id: Optional[int] = None,
        sort: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """List notes with offset pagination (v1).

        Returns a tuple of (items, pagination_info). The pagination dict mirrors
        Pipedrive's `additional_data.pagination` shape (start, limit,
        more_items_in_collection, next_start).
        """
        logger.info(
            f"NoteClient: listing notes (limit={limit}, start={start})"
        )
        if limit < 1 or limit > 500:
            raise ValueError(f"Invalid limit: {limit}. Must be between 1 and 500.")
        if start < 0:
            raise ValueError(f"Invalid start: {start}. Must be >= 0.")

        query_params: Dict[str, Any] = {
            "limit": limit,
            "start": start,
            "deal_id": deal_id,
            "person_id": person_id,
            "org_id": org_id,
            "lead_id": lead_id,
            "user_id": user_id,
            "sort": sort,
            "start_date": start_date,
            "end_date": end_date,
        }
        final_query_params = {k: v for k, v in query_params.items() if v is not None}

        response = await self.base_client.request(
            "GET", "/notes", query_params=final_query_params, version="v1"
        )
        items = response.get("data", []) or []
        pagination = (
            response.get("additional_data", {}).get("pagination", {})
            if isinstance(response.get("additional_data"), dict)
            else {}
        )
        logger.info(f"NoteClient: listed {len(items)} notes")
        return items, pagination
