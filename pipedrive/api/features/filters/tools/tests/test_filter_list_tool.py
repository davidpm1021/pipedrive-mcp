import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.filters.tools.filter_list_tool import (
    list_filters_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


def _make_mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.filters = MagicMock()
    mock_pipedrive_client.filters.list_filters = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_list_filters_no_type():
    ctx = _make_mock_context()
    items = [
        {"id": 1, "name": "Active NJ deals", "type": "deals"},
        {"id": 2, "name": "Renewal candidates", "type": "deals"},
    ]
    ctx.request_context.lifespan_context.pipedrive_client.filters.list_filters.return_value = items

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_filters_from_pipedrive(ctx=ctx)

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == items
    ctx.request_context.lifespan_context.pipedrive_client.filters.list_filters.assert_called_once_with(
        type_filter=None
    )


@pytest.mark.asyncio
async def test_list_filters_with_type():
    ctx = _make_mock_context()
    ctx.request_context.lifespan_context.pipedrive_client.filters.list_filters.return_value = []

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_filters_from_pipedrive(ctx=ctx, type_filter="deals")

    parsed = json.loads(result)
    assert parsed["success"] is True
    ctx.request_context.lifespan_context.pipedrive_client.filters.list_filters.assert_called_once_with(
        type_filter="deals"
    )


@pytest.mark.asyncio
async def test_list_filters_invalid_type():
    ctx = _make_mock_context()
    ctx.request_context.lifespan_context.pipedrive_client.filters.list_filters.side_effect = ValueError(
        "Invalid filter type: 'bogus'. Must be one of: ..."
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_filters_from_pipedrive(ctx=ctx, type_filter="bogus")

    parsed = json.loads(result)
    assert parsed["success"] is False
    assert "Invalid filter type" in parsed["error"]
