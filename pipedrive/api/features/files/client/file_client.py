from typing import Any, Dict, List, Optional, Tuple

from log_config import logger
from pipedrive.api.base_client import BaseClient


class FileClient:
    """Client for Pipedrive File API endpoints (v1, read-only metadata)."""

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    async def list_files(
        self,
        limit: int = 100,
        start: int = 0,
        deal_id: Optional[int] = None,
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """List file metadata with offset pagination.

        Note: Pipedrive's GET /files endpoint does not natively filter by
        deal_id/person_id/org_id; those filters are applied client-side here.
        For large file collections, use start/limit and filter in the caller.
        """
        logger.info(
            f"FileClient: listing files (limit={limit}, start={start}, "
            f"deal_id={deal_id}, person_id={person_id}, org_id={org_id})"
        )
        if limit < 1 or limit > 500:
            raise ValueError(f"Invalid limit: {limit}. Must be between 1 and 500.")
        if start < 0:
            raise ValueError(f"Invalid start: {start}. Must be >= 0.")

        query_params: Dict[str, Any] = {
            "limit": limit,
            "start": start,
            "sort": sort,
        }
        final_query_params = {k: v for k, v in query_params.items() if v is not None}

        response = await self.base_client.request(
            "GET", "/files", query_params=final_query_params, version="v1"
        )
        items = response.get("data", []) or []
        pagination = (
            response.get("additional_data", {}).get("pagination", {})
            if isinstance(response.get("additional_data"), dict)
            else {}
        )

        # Client-side filter by entity link if requested
        if deal_id is not None:
            items = [f for f in items if f.get("deal_id") == deal_id]
        if person_id is not None:
            items = [f for f in items if f.get("person_id") == person_id]
        if org_id is not None:
            items = [f for f in items if f.get("org_id") == org_id]

        return items, pagination

    async def get_file_metadata(self, file_id: int) -> Dict[str, Any]:
        """Get the metadata record for a single file.

        Returns the metadata only (name, size, MIME type, attached entity IDs,
        download URL, etc.) — not the file contents.
        """
        logger.info(f"FileClient: getting file metadata {file_id}")
        if file_id <= 0:
            raise ValueError(
                f"Invalid file_id: {file_id}. Must be a positive integer."
            )
        response = await self.base_client.request(
            "GET", f"/files/{file_id}", version="v1"
        )
        return response.get("data", {}) or {}
