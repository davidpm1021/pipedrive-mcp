from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("notes")
async def get_note_from_pipedrive(ctx: Context, id: str) -> str:
    """Gets a note from Pipedrive CRM by ID.

    Retrieves the full record for a single note, including its content, the
    entities it's attached to, and pin flags.

    Format requirements:
    - id: Note ID as a numeric string (e.g., "123")

    Example:
    ```
    get_note_from_pipedrive(id="123")
    ```

    Args:
        ctx: Context object provided by the MCP server
        id: ID of the note to retrieve

    Returns:
        JSON formatted response with the note data or error message
    """
    logger.info(f"Tool 'get_note_from_pipedrive' ENTERED with id='{id}'")
    sanitized = sanitize_inputs({"id": id})
    id_str = sanitized["id"]

    note_id, err = convert_id_string(id_str, "note_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    if note_id is None:
        return format_tool_response(False, error_message="Note ID is required")

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        data = await pd_mcp_ctx.pipedrive_client.notes.get_note(note_id=note_id)
        if not data:
            return format_tool_response(
                False, error_message=f"Note with ID {note_id} not found"
            )
        logger.info(f"Successfully retrieved note with ID: {note_id}")
        return format_tool_response(True, data=data)
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error getting note {note_id}: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting note {note_id}: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
