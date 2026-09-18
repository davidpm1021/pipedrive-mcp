from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("filters")
async def list_filters_from_pipedrive(
    ctx: Context, type_filter: Optional[str] = None
) -> str:
    """Lists saved Pipedrive filters, optionally narrowed to one entity type.

    Returns the user-defined saved filters configured in Pipedrive. Each filter
    has an id, name, type (deals/leads/people/etc), and the filter conditions.
    Use this to discover what filter_id values are available before passing
    one to other list tools (list_deals, list_persons, etc.).

    Format requirements:
    - type_filter: Optional. One of: "deals", "leads", "people", "org",
      "products", "activity", "projects". Omit to list all filters.

    Example:
    ```
    list_filters_from_pipedrive(type_filter="deals")
    ```

    Args:
        ctx: Context object provided by the MCP server
        type_filter: Optional entity type to narrow the filter list to

    Returns:
        JSON formatted response with the filter list or error message
    """
    logger.info(f"Tool 'list_filters_from_pipedrive' ENTERED with type_filter='{type_filter}'")
    sanitized = sanitize_inputs({"type_filter": type_filter})

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        items = await pd_mcp_ctx.pipedrive_client.filters.list_filters(
            type_filter=sanitized["type_filter"]
        )
        logger.info(f"Successfully retrieved {len(items)} filters")
        return format_tool_response(True, data={"items": items})
    except ValueError as e:
        logger.error(f"Validation error in list_filters_from_pipedrive: {e}")
        return format_tool_response(False, error_message=str(e))
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error listing filters: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error listing filters: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
