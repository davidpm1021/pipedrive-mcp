from typing import Any, Dict, List, Optional, Tuple

from log_config import logger
from pipedrive.api.base_client import BaseClient


class PipelineClient:
    """Client for Pipedrive Pipeline and Stage API endpoints (v1, read-only)."""

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    async def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all pipelines.

        Pipedrive's v1 /pipelines endpoint returns the full set without pagination.
        """
        logger.info("PipelineClient: listing pipelines")
        response = await self.base_client.request("GET", "/pipelines", version="v1")
        return response.get("data", []) or []

    async def get_pipeline(self, pipeline_id: int) -> Dict[str, Any]:
        """Get a single pipeline by ID."""
        logger.info(f"PipelineClient: getting pipeline {pipeline_id}")
        if pipeline_id <= 0:
            raise ValueError(
                f"Invalid pipeline_id: {pipeline_id}. Must be a positive integer."
            )
        response = await self.base_client.request(
            "GET", f"/pipelines/{pipeline_id}", version="v1"
        )
        return response.get("data", {}) or {}

    async def list_stages(
        self, pipeline_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List all stages, optionally filtered by pipeline_id."""
        logger.info(f"PipelineClient: listing stages (pipeline_id={pipeline_id})")
        query_params: Dict[str, Any] = {}
        if pipeline_id is not None:
            if pipeline_id <= 0:
                raise ValueError(
                    f"Invalid pipeline_id: {pipeline_id}. Must be a positive integer."
                )
            query_params["pipeline_id"] = pipeline_id

        response = await self.base_client.request(
            "GET",
            "/stages",
            query_params=query_params if query_params else None,
            version="v1",
        )
        return response.get("data", []) or []

    async def get_stage(self, stage_id: int) -> Dict[str, Any]:
        """Get a single stage by ID."""
        logger.info(f"PipelineClient: getting stage {stage_id}")
        if stage_id <= 0:
            raise ValueError(
                f"Invalid stage_id: {stage_id}. Must be a positive integer."
            )
        response = await self.base_client.request(
            "GET", f"/stages/{stage_id}", version="v1"
        )
        return response.get("data", {}) or {}

    async def list_deals_in_pipeline(
        self,
        pipeline_id: int,
        limit: int = 100,
        start: int = 0,
        filter_id: Optional[int] = None,
        user_id: Optional[int] = None,
        everyone: Optional[int] = None,
        stage_id: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """List deals in a pipeline with offset pagination (v1).

        Returns a tuple of (items, pagination_info).
        """
        logger.info(
            f"PipelineClient: listing deals in pipeline {pipeline_id} (limit={limit}, start={start})"
        )
        if pipeline_id <= 0:
            raise ValueError(
                f"Invalid pipeline_id: {pipeline_id}. Must be a positive integer."
            )
        if limit < 1 or limit > 500:
            raise ValueError(f"Invalid limit: {limit}. Must be between 1 and 500.")
        if start < 0:
            raise ValueError(f"Invalid start: {start}. Must be >= 0.")

        query_params: Dict[str, Any] = {
            "limit": limit,
            "start": start,
            "filter_id": filter_id,
            "user_id": user_id,
            "everyone": everyone,
            "stage_id": stage_id,
        }
        final_query_params = {k: v for k, v in query_params.items() if v is not None}

        response = await self.base_client.request(
            "GET",
            f"/pipelines/{pipeline_id}/deals",
            query_params=final_query_params,
            version="v1",
        )
        items = response.get("data", []) or []
        pagination = (
            response.get("additional_data", {}).get("pagination", {})
            if isinstance(response.get("additional_data"), dict)
            else {}
        )
        logger.info(
            f"PipelineClient: listed {len(items)} deals in pipeline {pipeline_id}"
        )
        return items, pagination
