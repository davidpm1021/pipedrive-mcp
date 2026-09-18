import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.notes.tools.note_create_tool import (
    create_note_in_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.notes = MagicMock()
    mock_pipedrive_client.notes.create_note = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_create_note_success(mock_context):
    expected = {
        "id": 99,
        "content": "Discussed Q2 renewal",
        "deal_id": 42,
        "user_id": 1,
    }
    mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await create_note_in_pipedrive(
            ctx=mock_context,
            content="Discussed Q2 renewal",
            deal_id="42",
        )

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"] == expected
    assert parsed["error"] is None
    mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.assert_called_once_with(
        content="Discussed Q2 renewal",
        deal_id=42,
    )


@pytest.mark.asyncio
async def test_create_note_requires_entity_link(mock_context):
    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await create_note_in_pipedrive(
            ctx=mock_context,
            content="Orphaned note",
        )

    parsed = json.loads(result)
    assert parsed["success"] is False
    assert "deal_id, person_id, org_id, or lead_id" in parsed["error"]
    mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.assert_not_called()
