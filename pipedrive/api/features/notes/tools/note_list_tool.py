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


@tool("notes")
async def list_notes_from_pipedrive(
    ctx: Context,
    limit_str: Optional[str] = "100",
    start_str: Optional[str] = "0",
    deal_id_str: Optional[str] = None,
    person_id_str: Optional[str] = None,
    org_id_str: Optional[str] = None,
    lead_id_str: Optional[str] = None,
    user_id_str: Optional[str] = None,
    sort: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """Lists notes from Pipedrive CRM with filtering and pagination.

    Retrieves notes with optional filters by attached entity (deal, person, org,
    lead, user) and date range. Pagination uses offset (`start`) since the
    Pipedrive Notes endpoint is v1.

    Format requirements:
    - limit_str: Numeric string between 1-500 (default "100")
    - start_str: Numeric offset for pagination (default "0")
    - deal_id_str, person_id_str, org_id_str, user_id_str: Numeric strings (e.g., "123")
    - lead_id_str: UUID string (e.g., "123e4567-e89b-12d3-a456-426614174000")
    - sort: Field name with optional direction (e.g., "id ASC", "update_time DESC")
    - start_date, end_date: ISO date strings (YYYY-MM-DD) — filters by add_time

    Example:
    ```
    list_notes_from_pipedrive(
        limit_str="50",
        deal_id_str="42",
        sort="update_time DESC"
    )
    ```

    Args:
        ctx: Context object provided by the MCP server
        limit_str: Maximum number of results to return (default "100", max "500")
        start_str: Pagination offset (default "0")
        deal_id_str: Filter by deal ID
        person_id_str: Filter by person ID
        org_id_str: Filter by organization ID
        lead_id_str: Filter by lead UUID
        user_id_str: Filter by note owner user ID
        sort: Sort spec (e.g., "id ASC")
        start_date: Lower bound on add_time (YYYY-MM-DD)
        end_date: Upper bound on add_time (YYYY-MM-DD)

    Returns:
        JSON formatted response with note list and pagination info, or error message
    """
    logger.info(f"Tool 'list_notes_from_pipedrive' ENTERED with limit={limit_str}, start={start_str}")
    sanitized = sanitize_inputs({
        "limit_str": limit_str,
        "start_str": start_str,
        "deal_id_str": deal_id_str,
        "person_id_str": person_id_str,
        "org_id_str": org_id_str,
        "lead_id_str": lead_id_str,
        "user_id_str": user_id_str,
        "sort": sort,
        "start_date": start_date,
        "end_date": end_date,
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
                return format_tool_response(
                    False, error_message="start must be >= 0"
                )
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
    user_id, err = convert_id_string(sanitized["user_id_str"], "user_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    lead_uuid, err = validate_uuid_string(
        sanitized["lead_id_str"], "lead_id", "123e4567-e89b-12d3-a456-426614174000"
    )
    if err:
        return format_tool_response(False, error_message=err)

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        items, pagination = await pd_mcp_ctx.pipedrive_client.notes.list_notes(
            limit=limit,
            start=start,
            deal_id=deal_id,
            person_id=person_id,
            org_id=org_id,
            lead_id=lead_uuid,
            user_id=user_id,
            sort=sanitized["sort"],
            start_date=sanitized["start_date"],
            end_date=sanitized["end_date"],
        )
        logger.info(f"Successfully retrieved {len(items)} notes")
        return format_tool_response(
            True,
            data={"items": items, "additional_data": {"pagination": pagination}},
        )
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error listing notes: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error listing notes: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
