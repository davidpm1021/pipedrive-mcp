from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("pipelines")
async def get_stage_from_pipedrive(ctx: Context, id: str) -> str:
    """Gets a stage from Pipedrive CRM by ID.

    Retrieves the full record for a single stage including its name, order_nr,
    deal probability, and the pipeline it belongs to.

    Format requirements:
    - id: Stage ID as a numeric string (e.g., "5")

    Example:
    ```
    get_stage_from_pipedrive(id="5")
    ```

    Args:
        ctx: Context object provided by the MCP server
        id: ID of the stage to retrieve

    Returns:
        JSON formatted response with the stage data or error message
    """
    logger.info(f"Tool 'get_stage_from_pipedrive' ENTERED with id='{id}'")
    sanitized = sanitize_inputs({"id": id})

    stage_id, err = convert_id_string(sanitized["id"], "stage_id", "5")
    if err:
        return format_tool_response(False, error_message=err)
    if stage_id is None:
        return format_tool_response(False, error_message="Stage ID is required")

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        data = await pd_mcp_ctx.pipedrive_client.pipelines.get_stage(stage_id=stage_id)
        if not data:
            return format_tool_response(
                False, error_message=f"Stage with ID {stage_id} not found"
            )
        logger.info(f"Successfully retrieved stage with ID: {stage_id}")
        return format_tool_response(True, data=data)
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error getting stage {stage_id}: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting stage {stage_id}: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
