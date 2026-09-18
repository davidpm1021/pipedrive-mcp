import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.pipelines.tools.pipeline_get_tool import (
    get_pipeline_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.pipelines = MagicMock()
    mock_pipedrive_client.pipelines.get_pipeline = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_get_pipeline_success(mock_context):
    expected = {"id": 1, "name": "Outbound", "active": True, "order_nr": 0}
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.get_pipeline.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await get_pipeline_from_pipedrive(ctx=mock_context, id="1")

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"] == expected
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.get_pipeline.assert_called_once_with(
        pipeline_id=1
    )
