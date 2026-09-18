import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.users.tools.user_list_tool import list_users_from_pipedrive
from pipedrive.api.features.users.tools.user_get_tool import get_user_from_pipedrive
from pipedrive.api.pipedrive_context import PipedriveMCPContext


def _make_mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.users = MagicMock()
    mock_pipedrive_client.users.list_users = AsyncMock()
    mock_pipedrive_client.users.get_user = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_list_users_success():
    ctx = _make_mock_context()
    expected = [
        {"id": 1, "name": "Aaron", "email": "aaron@ngpf.org", "active_flag": True},
        {"id": 2, "name": "Beth", "email": "beth@ngpf.org", "active_flag": True},
    ]
    ctx.request_context.lifespan_context.pipedrive_client.users.list_users.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_users_from_pipedrive(ctx=ctx)

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == expected


@pytest.mark.asyncio
async def test_get_user_success():
    ctx = _make_mock_context()
    expected = {"id": 1, "name": "Aaron", "email": "aaron@ngpf.org"}
    ctx.request_context.lifespan_context.pipedrive_client.users.get_user.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await get_user_from_pipedrive(ctx=ctx, id="1")

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"] == expected
    ctx.request_context.lifespan_context.pipedrive_client.users.get_user.assert_called_once_with(
        user_id=1
    )
