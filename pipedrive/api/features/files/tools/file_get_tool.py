from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("files")
async def get_file_metadata_from_pipedrive(ctx: Context, id: str) -> str:
    """Gets file metadata from Pipedrive CRM by file ID.

    Returns the metadata record for a single file (name, size, MIME type,
    attached entity IDs, download URL, add_time) — not the file contents.

    Format requirements:
    - id: File ID as a numeric string (e.g., "123")

    Example:
    ```
    get_file_metadata_from_pipedrive(id="123")
    ```

    Args:
        ctx: Context object provided by the MCP server
        id: ID of the file whose metadata to retrieve

    Returns:
        JSON formatted response with the file metadata or error message
    """
    logger.info(f"Tool 'get_file_metadata_from_pipedrive' ENTERED with id='{id}'")
    sanitized = sanitize_inputs({"id": id})

    file_id, err = convert_id_string(sanitized["id"], "file_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    if file_id is None:
        return format_tool_response(False, error_message="File ID is required")

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        data = await pd_mcp_ctx.pipedrive_client.files.get_file_metadata(file_id=file_id)
        if not data:
            return format_tool_response(
                False, error_message=f"File with ID {file_id} not found"
            )
        logger.info(f"Successfully retrieved file metadata for ID: {file_id}")
        return format_tool_response(True, data=data)
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error getting file {file_id}: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting file {file_id}: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
