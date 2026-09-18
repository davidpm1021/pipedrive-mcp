from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("users")
async def get_user_from_pipedrive(ctx: Context, id: str) -> str:
    """Gets a user from Pipedrive CRM by ID.

    Retrieves the full record for a single user including name, email, role,
    timezone, language, and active flag.

    Format requirements:
    - id: User ID as a numeric string (e.g., "1")

    Example:
    ```
    get_user_from_pipedrive(id="1")
    ```

    Args:
        ctx: Context object provided by the MCP server
        id: ID of the user to retrieve

    Returns:
        JSON formatted response with the user data or error message
    """
    logger.info(f"Tool 'get_user_from_pipedrive' ENTERED with id='{id}'")
    sanitized = sanitize_inputs({"id": id})

    user_id, err = convert_id_string(sanitized["id"], "user_id", "1")
    if err:
        return format_tool_response(False, error_message=err)
    if user_id is None:
        return format_tool_response(False, error_message="User ID is required")

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        data = await pd_mcp_ctx.pipedrive_client.users.get_user(user_id=user_id)
        if not data:
            return format_tool_response(
                False, error_message=f"User with ID {user_id} not found"
            )
        logger.info(f"Successfully retrieved user with ID: {user_id}")
        return format_tool_response(True, data=data)
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error getting user {user_id}: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting user {user_id}: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
