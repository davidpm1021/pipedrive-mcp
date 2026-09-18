import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.custom_fields.tools.deal_fields_list_tool import (
    list_deal_fields_from_pipedrive,
)
from pipedrive.api.features.custom_fields.tools.person_fields_list_tool import (
    list_person_fields_from_pipedrive,
)
from pipedrive.api.features.custom_fields.tools.org_fields_list_tool import (
    list_org_fields_from_pipedrive,
)
from pipedrive.api.features.custom_fields.tools.lead_fields_list_tool import (
    list_lead_fields_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


def _make_mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.custom_fields = MagicMock()
    mock_pipedrive_client.custom_fields.list_deal_fields = AsyncMock()
    mock_pipedrive_client.custom_fields.list_person_fields = AsyncMock()
    mock_pipedrive_client.custom_fields.list_org_fields = AsyncMock()
    mock_pipedrive_client.custom_fields.list_lead_fields = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_list_deal_fields_success():
    ctx = _make_mock_context()
    items = [
        {"id": 1, "key": "title", "name": "Title", "field_type": "varchar"},
        {
            "id": 100,
            "key": "abc123def",
            "name": "District",
            "field_type": "enum",
            "options": [{"id": 1, "label": "NJ"}, {"id": 2, "label": "NY"}],
        },
    ]
    pagination = {"start": 0, "limit": 100, "more_items_in_collection": False}
    ctx.request_context.lifespan_context.pipedrive_client.custom_fields.list_deal_fields.return_value = (
        items,
        pagination,
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_deal_fields_from_pipedrive(ctx=ctx)

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == items
    assert parsed["data"]["additional_data"]["pagination"] == pagination
    ctx.request_context.lifespan_context.pipedrive_client.custom_fields.list_deal_fields.assert_called_once_with(
        limit=100, start=0
    )


@pytest.mark.asyncio
async def test_list_person_fields_success():
    ctx = _make_mock_context()
    ctx.request_context.lifespan_context.pipedrive_client.custom_fields.list_person_fields.return_value = (
        [{"id": 1, "key": "name", "name": "Name"}],
        {},
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_person_fields_from_pipedrive(ctx=ctx, limit_str="50")

    parsed = json.loads(result)
    assert parsed["success"] is True
    ctx.request_context.lifespan_context.pipedrive_client.custom_fields.list_person_fields.assert_called_once_with(
        limit=50, start=0
    )


@pytest.mark.asyncio
async def test_list_org_fields_success():
    ctx = _make_mock_context()
    ctx.request_context.lifespan_context.pipedrive_client.custom_fields.list_org_fields.return_value = (
        [{"id": 1, "key": "address", "name": "Address"}],
        {},
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_org_fields_from_pipedrive(ctx=ctx, start_str="100")

    parsed = json.loads(result)
    assert parsed["success"] is True
    ctx.request_context.lifespan_context.pipedrive_client.custom_fields.list_org_fields.assert_called_once_with(
        limit=100, start=100
    )


@pytest.mark.asyncio
async def test_list_lead_fields_success():
    ctx = _make_mock_context()
    items = [
        {"id": 1, "key": "title", "name": "Title", "field_type": "varchar"},
        {
            "id": 100,
            "key": "abc123def",
            "name": "Lead Outreach Status",
            "field_type": "enum",
            "options": [{"id": 1, "label": "Not Started"}, {"id": 2, "label": "In Progress"}],
        },
    ]
    ctx.request_context.lifespan_context.pipedrive_client.custom_fields.list_lead_fields.return_value = (
        items,
        {},
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_lead_fields_from_pipedrive(ctx=ctx)

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == items
    ctx.request_context.lifespan_context.pipedrive_client.custom_fields.list_lead_fields.assert_called_once_with(
        limit=100, start=0
    )
