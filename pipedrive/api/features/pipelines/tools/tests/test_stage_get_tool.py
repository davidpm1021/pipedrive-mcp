import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.pipelines.tools.stage_get_tool import (
    get_stage_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.pipelines = MagicMock()
    mock_pipedrive_client.pipelines.get_stage = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_get_stage_success(mock_context):
    expected = {"id": 5, "name": "Qualified", "pipeline_id": 1, "order_nr": 0}
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.get_stage.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await get_stage_from_pipedrive(ctx=mock_context, id="5")

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"] == expected
    mock_context.request_context.lifespan_context.pipedrive_client.pipelines.get_stage.assert_called_once_with(
        stage_id=5
    )
