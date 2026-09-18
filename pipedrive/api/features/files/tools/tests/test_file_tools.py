import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from pipedrive.api.features.files.tools.file_list_tool import list_files_from_pipedrive
from pipedrive.api.features.files.tools.file_get_tool import (
    get_file_metadata_from_pipedrive,
)
from pipedrive.api.pipedrive_context import PipedriveMCPContext


def _make_mock_context():
    mock_ctx = MagicMock(spec=Context)
    mock_pipedrive_client = MagicMock()
    mock_pipedrive_client.files = MagicMock()
    mock_pipedrive_client.files.list_files = AsyncMock()
    mock_pipedrive_client.files.get_file_metadata = AsyncMock()

    mock_mcp_ctx = MagicMock(spec=PipedriveMCPContext)
    mock_mcp_ctx.pipedrive_client = mock_pipedrive_client
    mock_ctx.request_context.lifespan_context = mock_mcp_ctx
    return mock_ctx


@pytest.mark.asyncio
async def test_list_files_success():
    ctx = _make_mock_context()
    items = [
        {"id": 1, "name": "contract.pdf", "deal_id": 42, "file_size": 1024},
        {"id": 2, "name": "proposal.docx", "deal_id": 42, "file_size": 2048},
    ]
    pagination = {"start": 0, "limit": 100, "more_items_in_collection": False}
    ctx.request_context.lifespan_context.pipedrive_client.files.list_files.return_value = (
        items,
        pagination,
    )

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await list_files_from_pipedrive(ctx=ctx, deal_id_str="42")

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == items
    ctx.request_context.lifespan_context.pipedrive_client.files.list_files.assert_called_once_with(
        limit=100,
        start=0,
        deal_id=42,
        person_id=None,
        org_id=None,
        sort=None,
    )


@pytest.mark.asyncio
async def test_get_file_metadata_success():
    ctx = _make_mock_context()
    expected = {
        "id": 1,
        "name": "contract.pdf",
        "deal_id": 42,
        "file_size": 1024,
        "url": "https://...",
    }
    ctx.request_context.lifespan_context.pipedrive_client.files.get_file_metadata.return_value = expected

    with patch(
        "pipedrive.api.features.tool_registry.registry.is_feature_enabled",
        return_value=True,
    ):
        result = await get_file_metadata_from_pipedrive(ctx=ctx, id="1")

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"] == expected
    ctx.request_context.lifespan_context.pipedrive_client.files.get_file_metadata.assert_called_once_with(
        file_id=1
    )
