import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.pipelines.tools.pipeline_deals_list_tool import (
    list_deals_in_pipeline_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.pipelines = MagicMock()
    mock_pipedrive_client.pipelines.list_deals_in_pipeline = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_list_deals_in_pipeline_success(mock_context):
    items = [
        {"id": 100, "title": "Lenape Public Schools renewal", "pipeline_id": 1, "stage_id": 5},
        {"id": 101, "title": "Acme renewal", "pipeline_id": 1, "stage_id": 6},
    ]
    pagination = {"start": 0, "limit": 100, "more_items_in_collection": False}
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.list_deals_in_pipeline.return_value = (
        items,
        pagination,
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_deals_in_pipeline_from_pipedrive(
            ctx=mock_context,
            pipeline_id="1",
            limit_str="50",
            stage_id_str="5",
        )

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == items
    assert parsed["data"]["additional_data"]["pagination"] == pagination
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.list_deals_in_pipeline.assert_called_once_with(
        pipeline_id=1,
        limit=50,
        start=0,
        filter_id=None,
        user_id=None,
        stage_id=5,
        everyone=None,
    )


@pytest.mark.asyncio
async def test_list_deals_in_pipeline_requires_pipeline_id(mock_context):
    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_deals_in_pipeline_from_pipedrive(
            ctx=mock_context, pipeline_id=""
        )

    parsed = json.loads(result)
    assert parsed["success"] is False
    assert "pipeline_id is required" in parsed["error"]
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.list_deals_in_pipeline.assert_not_called()
