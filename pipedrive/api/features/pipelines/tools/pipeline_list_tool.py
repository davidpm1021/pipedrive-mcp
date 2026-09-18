from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("pipelines")
async def list_pipelines_from_pipedrive(ctx: Context) -> str:
    """Lists all pipelines from Pipedrive CRM.

    Returns every pipeline configured in the Pipedrive account. Pipedrive's
    /pipelines endpoint does not paginate, so the full set is returned.

    Format requirements:
    - No parameters required.

    Example:
    ```
    list_pipelines_from_pipedrive()
    ```

    Args:
        ctx: Context object provided by the MCP server

    Returns:
        JSON formatted response with the list of pipelines or error message
    """
    logger.info("Tool 'list_pipelines_from_pipedrive' ENTERED")
    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        items = await pd_mcp_ctx.pipedrive_client.pipelines.list_pipelines()
        logger.info(f"Successfully retrieved {len(items)} pipelines")
        return format_tool_response(True, data={"items": items})
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error listing pipelines: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error listing pipelines: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
