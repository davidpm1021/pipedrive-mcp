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
async def update_note_in_pipedrive(
    ctx: Context,
    id: str,
    content: Optional[str] = None,
    deal_id: Optional[str] = None,
    person_id: Optional[str] = None,
    org_id: Optional[str] = None,
    lead_id: Optional[str] = None,
    user_id: Optional[str] = None,
    pinned_to_deal_flag: Optional[bool] = None,
    pinned_to_person_flag: Optional[bool] = None,
    pinned_to_organization_flag: Optional[bool] = None,
    pinned_to_lead_flag: Optional[bool] = None,
) -> str:
    """Updates an existing note in Pipedrive CRM.

    Updates one or more fields of a note. The note ID is required, and at least
    one other field must be provided.

    Format requirements:
    - id: Note ID as a numeric string (e.g., "123")
    - deal_id, person_id, org_id, user_id: Numeric strings (e.g., "123")
    - lead_id: UUID string (e.g., "123e4567-e89b-12d3-a456-426614174000")
    - content: New note body (plain text or HTML)
    - pinned_*_flag: Booleans

    Example:
    ```
    update_note_in_pipedrive(
        id="123",
        content="Updated: discussed Q2 AND Q3 renewal",
        pinned_to_deal_flag=true
    )
    ```

    Args:
        ctx: Context object provided by the MCP server
        id: ID of the note to update
        content: New note body
        deal_id: Numeric ID of the deal to attach the note to
        person_id: Numeric ID of the person to attach the note to
        org_id: Numeric ID of the organization to attach the note to
        lead_id: UUID of the lead to attach the note to
        user_id: Numeric ID of the user who owns the note
        pinned_to_deal_flag: Whether to pin the note to the deal
        pinned_to_person_flag: Whether to pin the note to the person
        pinned_to_organization_flag: Whether to pin the note to the organization
        pinned_to_lead_flag: Whether to pin the note to the lead

    Returns:
        JSON formatted response with the updated note data or error message
    """
    logger.debug(f"Tool 'update_note_in_pipedrive' ENTERED with id='{id}'")
    sanitized = sanitize_inputs({
        "id": id,
        "content": content,
        "deal_id": deal_id,
        "person_id": person_id,
        "org_id": org_id,
        "lead_id": lead_id,
        "user_id": user_id,
    })

    note_id, err = convert_id_string(sanitized["id"], "note_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    if note_id is None:
        return format_tool_response(False, error_message="Note ID is required")

    update_fields = {}

    if sanitized["content"] is not None:
        update_fields["content"] = sanitized["content"]

    deal_id_int, err = convert_id_string(sanitized["deal_id"], "deal_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    if deal_id_int is not None:
        update_fields["deal_id"] = deal_id_int

    person_id_int, err = convert_id_string(sanitized["person_id"], "person_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    if person_id_int is not None:
        update_fields["person_id"] = person_id_int

    org_id_int, err = convert_id_string(sanitized["org_id"], "org_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    if org_id_int is not None:
        update_fields["org_id"] = org_id_int

    user_id_int, err = convert_id_string(sanitized["user_id"], "user_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    if user_id_int is not None:
        update_fields["user_id"] = user_id_int

    lead_uuid, err = validate_uuid_string(
        sanitized["lead_id"], "lead_id", "123e4567-e89b-12d3-a456-426614174000"
    )
    if err:
        return format_tool_response(False, error_message=err)
    if lead_uuid is not None:
        update_fields["lead_id"] = lead_uuid

    for flag_name, flag_value in (
        ("pinned_to_deal_flag", pinned_to_deal_flag),
        ("pinned_to_person_flag", pinned_to_person_flag),
        ("pinned_to_organization_flag", pinned_to_organization_flag),
        ("pinned_to_lead_flag", pinned_to_lead_flag),
    ):
        if flag_value is not None:
            update_fields[flag_name] = flag_value

    if not update_fields:
        return format_tool_response(
            False, error_message="At least one field must be provided for updating a note"
        )

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        updated = await pd_mcp_ctx.pipedrive_client.notes.update_note(
            note_id=note_id, **update_fields
        )
        logger.info(f"Successfully updated note with ID: {note_id}")
        return format_tool_response(True, data=updated)
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error updating note {note_id}: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error updating note {note_id}: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
