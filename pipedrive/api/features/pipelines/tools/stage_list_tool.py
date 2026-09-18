from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("pipelines")
async def list_stages_from_pipedrive(
    ctx: Context, pipeline_id: Optional[str] = None
) -> str:
    """Lists stages from Pipedrive CRM, optionally filtered by pipeline.

    Returns all stages across pipelines, or only stages within a specific
    pipeline if pipeline_id is provided. Stages have an order_nr that
    indicates their position in the pipeline.

    Format requirements:
    - pipeline_id: Optional numeric string (e.g., "1") — when provided, only
      stages in that pipeline are returned.

    Example:
    ```
    list_stages_from_pipedrive(pipeline_id="1")
    ```

    Args:
        ctx: Context object provided by the MCP server
        pipeline_id: Optional ID of the pipeline to filter by

    Returns:
        JSON formatted response with the list of stages or error message
    """
    logger.info(f"Tool 'list_stages_from_pipedrive' ENTERED with pipeline_id='{pipeline_id}'")
    sanitized = sanitize_inputs({"pipeline_id": pipeline_id})

    pipeline_id_int, err = convert_id_string(
        sanitized["pipeline_id"], "pipeline_id", "1"
    )
    if err:
        return format_tool_response(False, error_message=err)

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        items = await pd_mcp_ctx.pipedrive_client.pipelines.list_stages(
            pipeline_id=pipeline_id_int
        )
        logger.info(f"Successfully retrieved {len(items)} stages")
        return format_tool_response(True, data={"items": items})
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error listing stages: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error listing stages: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
