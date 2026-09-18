import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.notes.tools.note_list_tool import (
    list_notes_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.notes = MagicMock()
    mock_pipedrive_client.notes.list_notes = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_list_notes_success(mock_context):
    items = [
        {"id": 1, "content": "First note", "deal_id": 42},
        {"id": 2, "content": "Second note", "deal_id": 42},
    ]
    pagination = {"start": 0, "limit": 100, "more_items_in_collection": False}
    mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.return_value = (
        items,
        pagination,
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_notes_from_pipedrive(
            ctx=mock_context,
            limit_str="100",
            deal_id_str="42",
        )

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == items
    assert parsed["data"]["additional_data"]["pagination"] == pagination
    mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.assert_called_once_with(
        limit=100,
        start=0,
        deal_id=42,
        person_id=None,
        org_id=None,
        lead_id=None,
        user_id=None,
        sort=None,
        start_date=None,
        end_date=None,
    )
