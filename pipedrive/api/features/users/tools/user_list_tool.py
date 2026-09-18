from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("users")
async def list_users_from_pipedrive(ctx: Context) -> str:
    """Lists all users in the Pipedrive account.

    Returns every user with their id, name, email, and active flag. Use this
    to resolve a user's name (e.g. "Aaron") to the numeric ID required by
    other tools' owner_id parameters.

    Format requirements:
    - No parameters required.

    Example:
    ```
    list_users_from_pipedrive()
    ```

    Args:
        ctx: Context object provided by the MCP server

    Returns:
        JSON formatted response with the list of users or error message
    """
    logger.info("Tool 'list_users_from_pipedrive' ENTERED")
    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        items = await pd_mcp_ctx.pipedrive_client.users.list_users()
        logger.info(f"Successfully retrieved {len(items)} users")
        return format_tool_response(True, data={"items": items})
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error listing users: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error listing users: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
