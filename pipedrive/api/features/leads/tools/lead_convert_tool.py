from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import (
    convert_id_string,
    validate_uuid_string,
)
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("leads")
async def convert_lead_to_deal(
    ctx: Context,
    lead_id: str,
    pipeline_id: Optional[str] = None,
    stage_id: Optional[str] = None,
) -> str:
    """Converts a lead to a deal in Pipedrive CRM.

    This tool starts a server-side conversion job (Pipedrive v2 async API), polls
    the status endpoint until the job reaches a terminal state, and returns the
    new deal's ID on success. Polling uses a 1-second interval with a 30-second
    overall timeout.

    Format requirements:
    - lead_id: UUID string (e.g., "123e4567-e89b-12d3-a456-426614174000")
    - pipeline_id: Optional numeric string for the destination pipeline (e.g., "1")
    - stage_id: Optional numeric string for the destination stage (e.g., "5")

    Example:
    ```
    convert_lead_to_deal(
        lead_id="123e4567-e89b-12d3-a456-426614174000",
        pipeline_id="1",
        stage_id="5"
    )
    ```

    Args:
        ctx: Context object provided by the MCP server
        lead_id: UUID of the lead to convert
        pipeline_id: Optional ID of the pipeline to place the new deal in
        stage_id: Optional ID of the stage to place the new deal in

    Returns:
        JSON formatted response with the new deal_id and conversion metadata,
        or an error message if the conversion failed, was rejected, or timed out
    """
    logger.info(f"Tool 'convert_lead_to_deal' ENTERED with lead_id='{lead_id}'")
    sanitized = sanitize_inputs({
        "lead_id": lead_id,
        "pipeline_id": pipeline_id,
        "stage_id": stage_id,
    })

    lead_uuid, err = validate_uuid_string(
        sanitized["lead_id"], "lead_id", "123e4567-e89b-12d3-a456-426614174000"
    )
    if err:
        return format_tool_response(False, error_message=err)
    if lead_uuid is None:
        return format_tool_response(False, error_message="lead_id is required")

    pipeline_id_int, err = convert_id_string(
        sanitized["pipeline_id"], "pipeline_id", "1"
    )
    if err:
        return format_tool_response(False, error_message=err)
    stage_id_int, err = convert_id_string(sanitized["stage_id"], "stage_id", "5")
    if err:
        return format_tool_response(False, error_message=err)

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        result = await pd_mcp_ctx.pipedrive_client.lead_client.convert_lead_to_deal(
            lead_id=lead_uuid,
            pipeline_id=pipeline_id_int,
            stage_id=stage_id_int,
        )
        logger.info(
            f"Successfully converted lead {lead_uuid} to deal {result.get('deal_id')}"
        )
        return format_tool_response(True, data=result)
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error converting lead {lead_uuid}: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except ValueError as e:
        logger.error(f"Validation error converting lead {lead_uuid}: {e}")
        return format_tool_response(False, error_message=str(e))
    except Exception as e:
        logger.error(f"Unexpected error converting lead {lead_uuid}: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
