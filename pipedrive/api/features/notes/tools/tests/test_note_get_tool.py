import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.notes.tools.note_get_tool import get_note_from_pipedrive
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.notes = MagicMock()
    mock_pipedrive_client.notes.get_note = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_get_note_success(mock_context):
    expected = {"id": 99, "content": "Discussed Q2 renewal", "deal_id": 42}
    mock_context.request_context.lifespan_context.pipedrive_client.notes.get_note.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await get_note_from_pipedrive(ctx=mock_context, id="99")

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"] == expected
    mock_context.request_context.lifespan_context.pipedrive_client.notes.get_note.assert_called_once_with(
        note_id=99
    )


@pytest.mark.asyncio
async def test_get_note_not_found(mock_context):
    mock_context.request_context.lifespan_context.pipedrive_client.notes.get_note.return_value = {}

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await get_note_from_pipedrive(ctx=mock_context, id="99")

    parsed = json.loads(result)
    assert parsed["success"] is False
    assert "not found" in parsed["error"]
