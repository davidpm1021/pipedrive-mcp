from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import (
    format_tool_response,
    safe_split_to_list,
    sanitize_inputs,
)
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("persons")
async def list_persons_from_pipedrive(
    ctx: Context,
    limit_str: Optional[str] = "100",
    cursor: Optional[str] = None,
    filter_id_str: Optional[str] = None,
    owner_id_str: Optional[str] = None,
    org_id_str: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = None,
    include_fields_str: Optional[str] = None,
    custom_fields_keys_str: Optional[str] = None,
    updated_since: Optional[str] = None,
    updated_until: Optional[str] = None,
) -> str:
    """Lists persons from Pipedrive CRM with filtering and cursor pagination.

    Retrieves a list of persons with optional filters by owner, organization,
    saved filter, or update time. Pagination uses a cursor token returned in
    the previous response.

    Format requirements:
    - limit_str: Numeric string between 1-500 (default "100")
    - filter_id_str, owner_id_str, org_id_str: Numeric strings (e.g., "123")
    - sort_by: One of "id", "update_time", "add_time"
    - sort_direction: "asc" or "desc"
    - updated_since, updated_until: RFC3339 timestamps (e.g., "2026-01-01T00:00:00Z")
    - include_fields_str: Comma-separated list of additional fields
    - custom_fields_keys_str: Comma-separated list of custom field keys

    Example:
    ```
    list_persons_from_pipedrive(
        limit_str="50",
        owner_id_str="123",
        sort_by="update_time",
        sort_direction="desc"
    )
    ```

    Args:
        ctx: Context object provided by the MCP server
        limit_str: Maximum number of results (default "100", max "500")
        cursor: Pagination cursor for the next page (from previous response)
        filter_id_str: Numeric ID of a saved Pipedrive filter to apply
        owner_id_str: Filter by person owner ID
        org_id_str: Filter by associated organization ID
        sort_by: Field to sort by ("id", "update_time", "add_time")
        sort_direction: Sort direction ("asc", "desc")
        include_fields_str: Comma-separated list of additional fields to include
        custom_fields_keys_str: Comma-separated list of custom field keys to include
        updated_since: Lower bound on update time (RFC3339)
        updated_until: Upper bound on update time (RFC3339)

    Returns:
        JSON formatted response with the person list and next_cursor, or error message
    """
    logger.info(f"Tool 'list_persons_from_pipedrive' ENTERED with limit={limit_str}, cursor='{cursor}'")
    sanitized = sanitize_inputs({
        "limit_str": limit_str,
        "cursor": cursor,
        "filter_id_str": filter_id_str,
        "owner_id_str": owner_id_str,
        "org_id_str": org_id_str,
        "sort_by": sort_by,
        "sort_direction": sort_direction,
        "include_fields_str": include_fields_str,
        "custom_fields_keys_str": custom_fields_keys_str,
        "updated_since": updated_since,
        "updated_until": updated_until,
    })

    limit = 100
    if sanitized["limit_str"]:
        try:
            limit = int(sanitized["limit_str"])
            if limit < 1 or limit > 500:
                limit = min(max(limit, 1), 500)
        except ValueError:
            return format_tool_response(
                False,
                error_message=f"Invalid limit value: '{sanitized['limit_str']}'. Must be a numeric string between 1 and 500.",
            )

    filter_id, err = convert_id_string(sanitized["filter_id_str"], "filter_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    owner_id, err = convert_id_string(sanitized["owner_id_str"], "owner_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    org_id, err = convert_id_string(sanitized["org_id_str"], "org_id", "123")
    if err:
        return format_tool_response(False, error_message=err)

    valid_sort_fields = ["id", "update_time", "add_time"]
    if sanitized["sort_by"] and sanitized["sort_by"] not in valid_sort_fields:
        return format_tool_response(
            False,
            error_message=f"Invalid sort_by: '{sanitized['sort_by']}'. Must be one of: {', '.join(valid_sort_fields)}",
        )
    if sanitized["sort_direction"] and sanitized["sort_direction"] not in ("asc", "desc"):
        return format_tool_response(
            False,
            error_message=f"Invalid sort_direction: '{sanitized['sort_direction']}'. Must be 'asc' or 'desc'.",
        )

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        items, next_cursor = await pd_mcp_ctx.pipedrive_client.persons.list_persons(
            limit=limit,
            cursor=sanitized["cursor"],
            filter_id=filter_id,
            owner_id=owner_id,
            org_id=org_id,
            sort_by=sanitized["sort_by"],
            sort_direction=sanitized["sort_direction"],
            include_fields=safe_split_to_list(sanitized["include_fields_str"]),
            custom_fields_keys=safe_split_to_list(sanitized["custom_fields_keys_str"]),
            updated_since=sanitized["updated_since"],
            updated_until=sanitized["updated_until"],
        )
        logger.info(f"Successfully retrieved {len(items)} persons. Next cursor: '{next_cursor}'")
        return format_tool_response(
            True,
            data={
                "items": items,
                "additional_data": {"next_cursor": next_cursor} if next_cursor else {},
            },
        )
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error listing persons: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error listing persons: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
