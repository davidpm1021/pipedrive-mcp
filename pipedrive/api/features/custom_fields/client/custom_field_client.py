from typing import Any, Dict, List, Optional, Tuple

from log_config import logger
from pipedrive.api.base_client import BaseClient


class CustomFieldClient:
    """Client for Pipedrive custom field metadata endpoints (v1, read-only).

    Used to discover the custom fields configured on deals, persons, and
    organizations — including the API key (e.g. `abc123def...`), human-readable
    name, field_type, and (for enum/set fields) the option list.
    """

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    async def _list_fields(
        self,
        endpoint: str,
        limit: int,
        start: int,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if limit < 1 or limit > 500:
            raise ValueError(f"Invalid limit: {limit}. Must be between 1 and 500.")
        if start < 0:
            raise ValueError(f"Invalid start: {start}. Must be >= 0.")

        response = await self.base_client.request(
            "GET",
            endpoint,
            query_params={"limit": limit, "start": start},
            version="v1",
        )
        items = response.get("data", []) or []
        pagination = (
            response.get("additional_data", {}).get("pagination", {})
            if isinstance(response.get("additional_data"), dict)
            else {}
        )
        return items, pagination

    async def list_deal_fields(
        self, limit: int = 100, start: int = 0
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        logger.info(f"CustomFieldClient: listing deal fields (limit={limit}, start={start})")
        return await self._list_fields("/dealFields", limit, start)

    async def list_person_fields(
        self, limit: int = 100, start: int = 0
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        logger.info(f"CustomFieldClient: listing person fields (limit={limit}, start={start})")
        return await self._list_fields("/personFields", limit, start)

    async def list_org_fields(
        self, limit: int = 100, start: int = 0
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        logger.info(f"CustomFieldClient: listing organization fields (limit={limit}, start={start})")
        return await self._list_fields("/organizationFields", limit, start)

    async def list_lead_fields(
        self, limit: int = 100, start: int = 0
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        logger.info(f"CustomFieldClient: listing lead fields (limit={limit}, start={start})")
        return await self._list_fields("/leadFields", limit, start)
