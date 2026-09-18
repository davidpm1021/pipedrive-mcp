from typing import Any, Dict, List, Optional

from log_config import logger
from pipedrive.api.base_client import BaseClient


class FilterClient:
    """Client for Pipedrive saved filter endpoints (v1, read-only)."""

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    async def list_filters(
        self, type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List saved filters, optionally narrowed to one entity type.

        Args:
            type_filter: Pipedrive filter type. One of: "deals", "leads",
                "people", "org", "products", "activity", "projects". If
                omitted, returns filters across all types.
        """
        logger.info(f"FilterClient: listing filters (type={type_filter})")

        valid_types = {
            "deals", "leads", "people", "org", "products", "activity", "projects"
        }
        query_params: Dict[str, Any] = {}
        if type_filter is not None:
            if type_filter not in valid_types:
                raise ValueError(
                    f"Invalid filter type: '{type_filter}'. Must be one of: {sorted(valid_types)}"
                )
            query_params["type"] = type_filter

        response = await self.base_client.request(
            "GET",
            "/filters",
            query_params=query_params if query_params else None,
            version="v1",
        )
        return response.get("data", []) or []
