import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.pipelines.tools.stage_list_tool import (
    list_stages_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.pipelines = MagicMock()
    mock_pipedrive_client.pipelines.list_stages = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_list_stages_filtered_by_pipeline(mock_context):
    expected = [
        {"id": 5, "name": "Qualified", "pipeline_id": 1, "order_nr": 0},
        {"id": 6, "name": "Proposal", "pipeline_id": 1, "order_nr": 1},
    ]
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.list_stages.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_stages_from_pipedrive(ctx=mock_context, pipeline_id="1")

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == expected
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.list_stages.assert_called_once_with(
        pipeline_id=1
    )


@pytest.mark.asyncio
async def test_list_stages_no_filter(mock_context):
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.list_stages.return_value = []

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_stages_from_pipedrive(ctx=mock_context)

    parsed = json.loads(result)
    assert parsed["success"] is True
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.list_stages.assert_called_once_with(
        pipeline_id=None
    )
