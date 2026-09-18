import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.persons.tools.person_list_tool import (
    list_persons_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@pytest.fixture
def mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.persons = MagicMock()
    mock_pipedrive_client.persons.list_persons = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_list_persons_success(mock_context):
    items = [
        {"id": 1, "name": "Aaron Standish", "owner_id": 22141866},
        {"id": 2, "name": "Beth Tester", "owner_id": 22141866},
    ]
    next_cursor = "abc123"
    mock_context.request_context.lifespan_context.pipedrive_client.persons.list_persons.return_value = (
        items,
        next_cursor,
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_persons_from_pipedrive(
            ctx=mock_context, limit_str="50", owner_id_str="22141866"
        )

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == items
    assert parsed["data"]["additional_data"]["next_cursor"] == next_cursor
    mock_context.request_context.lifespan_context.pipedrive_client.persons.list_persons.assert_called_once_with(
        limit=50,
        cursor=None,
        filter_id=None,
        owner_id=22141866,
        org_id=None,
        sort_by=None,
        sort_direction=None,
        include_fields=None,
        custom_fields_keys=None,
        updated_since=None,
        updated_until=None,
    )
