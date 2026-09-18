from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("pipelines")
async def list_deals_in_pipeline_from_pipedrive(
    ctx: Context,
    pipeline_id: str,
    limit_str: Optional[str] = "100",
    start_str: Optional[str] = "0",
    filter_id_str: Optional[str] = None,
    user_id_str: Optional[str] = None,
    stage_id_str: Optional[str] = None,
    everyone_str: Optional[str] = None,
) -> str:
    """Lists deals belonging to a specific pipeline.

    Retrieves the deals in a given pipeline with offset pagination (v1).
    Useful for answering "show me deals in the Outbound pipeline" or
    "advance the next deal in the renewals pipeline".

    Format requirements:
    - pipeline_id: Required numeric string (e.g., "1")
    - limit_str: Numeric string between 1-500 (default "100")
    - start_str: Numeric offset for pagination (default "0")
    - filter_id_str, user_id_str, stage_id_str: Numeric strings (e.g., "123")
    - everyone_str: "1" to include deals from all users, "0" or omit for the
      authenticated user only

    Example:
    ```
    list_deals_in_pipeline_from_pipedrive(
        pipeline_id="1",
        limit_str="50",
        stage_id_str="3"
    )
    ```

    Args:
        ctx: Context object provided by the MCP server
        pipeline_id: ID of the pipeline whose deals should be listed
        limit_str: Maximum number of results (default "100", max "500")
        start_str: Pagination offset (default "0")
        filter_id_str: ID of a filter to apply
        user_id_str: ID of the user to filter by
        stage_id_str: ID of the stage to filter by
        everyone_str: "1" to include deals from all users

    Returns:
        JSON formatted response with the deal list and pagination info, or error message
    """
    logger.info(
        f"Tool 'list_deals_in_pipeline_from_pipedrive' ENTERED with pipeline_id='{pipeline_id}'"
    )
    sanitized = sanitize_inputs({
        "pipeline_id": pipeline_id,
        "limit_str": limit_str,
        "start_str": start_str,
        "filter_id_str": filter_id_str,
        "user_id_str": user_id_str,
        "stage_id_str": stage_id_str,
        "everyone_str": everyone_str,
    })

    pipeline_id_int, err = convert_id_string(
        sanitized["pipeline_id"], "pipeline_id", "1"
    )
    if err:
        return format_tool_response(False, error_message=err)
    if pipeline_id_int is None:
        return format_tool_response(False, error_message="pipeline_id is required")

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

    filter_id, err = convert_id_string(sanitized["filter_id_str"], "filter_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    user_id, err = convert_id_string(sanitized["user_id_str"], "user_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    stage_id, err = convert_id_string(sanitized["stage_id_str"], "stage_id", "123")
    if err:
        return format_tool_response(False, error_message=err)

    everyone = None
    if sanitized["everyone_str"] is not None:
        if sanitized["everyone_str"] not in ("0", "1"):
            return format_tool_response(
                False,
                error_message="everyone_str must be '0' or '1' if provided",
            )
        everyone = int(sanitized["everyone_str"])

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        items, pagination = await pd_mcp_ctx.pipedrive_client.pipelines.list_deals_in_pipeline(
            pipeline_id=pipeline_id_int,
            limit=limit,
            start=start,
            filter_id=filter_id,
            user_id=user_id,
            stage_id=stage_id,
            everyone=everyone,
        )
        logger.info(
            f"Successfully retrieved {len(items)} deals in pipeline {pipeline_id_int}"
        )
        return format_tool_response(
            True,
            data={"items": items, "additional_data": {"pagination": pagination}},
        )
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error listing deals in pipeline: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error listing deals in pipeline: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
