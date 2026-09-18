from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("files")
async def list_files_from_pipedrive(
    ctx: Context,
    limit_str: Optional[str] = "100",
    start_str: Optional[str] = "0",
    deal_id_str: Optional[str] = None,
    person_id_str: Optional[str] = None,
    org_id_str: Optional[str] = None,
    sort: Optional[str] = None,
) -> str:
    """Lists file metadata from Pipedrive CRM.

    Returns the metadata records for files (name, size, MIME type, attached
    entity IDs, download URL) — not the file contents themselves. Optional
    filters by attached entity (deal_id, person_id, org_id) are applied
    client-side after fetching the page.

    Format requirements:
    - limit_str: Numeric string between 1-500 (default "100")
    - start_str: Numeric offset for pagination (default "0")
    - deal_id_str, person_id_str, org_id_str: Numeric strings (e.g., "123")
    - sort: Field name with optional direction (e.g., "id ASC", "update_time DESC")

    Example:
    ```
    list_files_from_pipedrive(
        limit_str="50",
        deal_id_str="42"
    )
    ```

    Args:
        ctx: Context object provided by the MCP server
        limit_str: Maximum number of results (default "100", max "500")
        start_str: Pagination offset (default "0")
        deal_id_str: Filter by attached deal ID (client-side filter)
        person_id_str: Filter by attached person ID (client-side filter)
        org_id_str: Filter by attached organization ID (client-side filter)
        sort: Sort spec (e.g., "id ASC")

    Returns:
        JSON formatted response with the file metadata list and pagination info, or error message
    """
    logger.info(f"Tool 'list_files_from_pipedrive' ENTERED with limit={limit_str}, start={start_str}")
    sanitized = sanitize_inputs({
        "limit_str": limit_str,
        "start_str": start_str,
        "deal_id_str": deal_id_str,
        "person_id_str": person_id_str,
        "org_id_str": org_id_str,
        "sort": sort,
    })

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

    deal_id, err = convert_id_string(sanitized["deal_id_str"], "deal_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    person_id, err = convert_id_string(sanitized["person_id_str"], "person_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    org_id, err = convert_id_string(sanitized["org_id_str"], "org_id", "123")
    if err:
        return format_tool_response(False, error_message=err)

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        items, pagination = await pd_mcp_ctx.pipedrive_client.files.list_files(
            limit=limit,
            start=start,
            deal_id=deal_id,
            person_id=person_id,
            org_id=org_id,
            sort=sanitized["sort"],
        )
        logger.info(f"Successfully retrieved {len(items)} files")
        return format_tool_response(
            True,
            data={"items": items, "additional_data": {"pagination": pagination}},
        )
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error listing files: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error listing files: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
