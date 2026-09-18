import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.leads.tools.lead_convert_tool import convert_lead_to_deal
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.lead_client = MagicMock()
    mock_pipedrive_client.lead_client.convert_lead_to_deal = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_convert_lead_to_deal_success(mock_context):
    expected = {
        "deal_id": 555,
        "conversion_id": "conv-uuid-1",
        "status": "completed",
    }
    mock_context.request_context.lifespan_context.pipedrive_client.lead_client.convert_lead_to_deal.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await convert_lead_to_deal(
            ctx=mock_context,
            lead_id="123e4567-e89b-12d3-a456-426614174000",
            pipeline_id="1",
            stage_id="5",
        )

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"] == expected
    mock_context.request_context.lifespan_context.pipedrive_client.lead_client.convert_lead_to_deal.assert_called_once_with(
        lead_id="123e4567-e89b-12d3-a456-426614174000",
        pipeline_id=1,
        stage_id=5,
    )


@pytest.mark.asyncio
async def test_convert_lead_to_deal_failed_status(mock_context):
    mock_context.request_context.lifespan_context.pipedrive_client.lead_client.convert_lead_to_deal.side_effect = PipedriveAPIError(
        message="Lead-to-deal conversion failed: lead has no associated person or organization"
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await convert_lead_to_deal(
            ctx=mock_context,
            lead_id="123e4567-e89b-12d3-a456-426614174000",
        )

    parsed = json.loads(result)
    assert parsed["success"] is False
    assert "Pipedrive API error" in parsed["error"]
    assert "conversion failed" in parsed["error"]


@pytest.mark.asyncio
async def test_convert_lead_to_deal_invalid_uuid(mock_context):
    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await convert_lead_to_deal(
            ctx=mock_context,
            lead_id="not-a-uuid",
        )

    parsed = json.loads(result)
    assert parsed["success"] is False
    assert "lead_id must be a valid UUID" in parsed["error"]
    mock_context.request_context.lifespan_context.pipedrive_client.lead_client.convert_lead_to_deal.assert_not_called()
