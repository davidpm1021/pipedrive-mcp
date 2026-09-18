from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("custom_fields")
async def list_deal_fields_from_pipedrive(
    ctx: Context,
    limit_str: Optional[str] = "100",
    start_str: Optional[str] = "0",
) -> str:
    """Lists deal fields (standard and custom) from Pipedrive CRM.

    Returns the field metadata for deals: id, key (the API key used in
    create/update payloads, e.g. "abc123def..."), name, field_type, and the
    options list for enum/set fields. Use this to discover what custom fields
    are configured before creating or updating a deal.

    Format requirements:
    - limit_str: Numeric string between 1-500 (default "100")
    - start_str: Numeric offset for pagination (default "0")

    Example:
    ```
    list_deal_fields_from_pipedrive(limit_str="200")
    ```

    Args:
        ctx: Context object provided by the MCP server
        limit_str: Maximum number of results (default "100", max "500")
        start_str: Pagination offset (default "0")

    Returns:
        JSON formatted response with the deal field list and pagination info, or error message
    """
    return await _list_fields_impl(
        ctx, limit_str, start_str, "list_deal_fields_from_pipedrive", "list_deal_fields"
    )


async def _list_fields_impl(
    ctx: Context, limit_str: Optional[str], start_str: Optional[str], tool_name: str, method_name: str
) -> str:
    logger.info(f"Tool '{tool_name}' ENTERED with limit={limit_str}, start={start_str}")
    sanitized = sanitize_inputs({"limit_str": limit_str, "start_str": start_str})

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

    start = 0
    if sanitized["start_str"]:
        try:
            start = int(sanitized["start_str"])
            if start < 0:
                return format_tool_response(False, error_message="start must be >= 0")
        except ValueError:
            return format_tool_response(
                False,
                error_message=f"Invalid start value: '{sanitized['start_str']}'. Must be a non-negative numeric string.",
            )

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        method = getattr(pd_mcp_ctx.pipedrive_client.custom_fields, method_name)
        items, pagination = await method(limit=limit, start=start)
        logger.info(f"{tool_name}: retrieved {len(items)} fields")
        return format_tool_response(
            True,
            data={"items": items, "additional_data": {"pagination": pagination}},
        )
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error in {tool_name}: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in {tool_name}: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
