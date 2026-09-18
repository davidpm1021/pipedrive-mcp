from typing import Optional

from mcp.server.fastmcp import Context
from pydantic import ValidationError

from log_config import logger
from pipedrive.api.features.notes.models.note import Note
from pipedrive.api.features.shared.conversion.id_conversion import (
    convert_id_string,
    validate_uuid_string,
)
from pipedrive.api.features.shared.utils import format_tool_response, sanitize_inputs
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext


@tool("notes")
async def create_note_in_pipedrive(
    ctx: Context,
    content: str,
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
    """Creates a note in Pipedrive CRM.

    This tool creates a note attached to a deal, person, organization, or lead.
    At least one of deal_id, person_id, org_id, or lead_id must be provided.

    Format requirements:
    - content: Note body. Plain text or HTML (Pipedrive supports a subset of HTML).
    - deal_id, person_id, org_id, user_id: Numeric strings (e.g., "123")
    - lead_id: UUID string (e.g., "123e4567-e89b-12d3-a456-426614174000")
    - pinned_*_flag: Booleans. The matching entity ID must also be provided
      (e.g., to pin to a deal, set both deal_id and pinned_to_deal_flag=true).

    Example:
    ```
    create_note_in_pipedrive(
        content="Discussed Q2 renewal on call",
        deal_id="42",
        pinned_to_deal_flag=true
    )
    ```

    Args:
        ctx: Context object provided by the MCP server
        content: The note body
        deal_id: Numeric ID of the deal to attach the note to
        person_id: Numeric ID of the person to attach the note to
        org_id: Numeric ID of the organization to attach the note to
        lead_id: UUID of the lead to attach the note to
        user_id: Numeric ID of the user who owns the note (defaults to API token user)
        pinned_to_deal_flag: Whether to pin the note to the deal
        pinned_to_person_flag: Whether to pin the note to the person
        pinned_to_organization_flag: Whether to pin the note to the organization
        pinned_to_lead_flag: Whether to pin the note to the lead

    Returns:
        JSON formatted response with the created note data or error message
    """
    logger.debug(f"Tool 'create_note_in_pipedrive' ENTERED, deal_id={deal_id}, person_id={person_id}, org_id={org_id}, lead_id={lead_id}")

    sanitized = sanitize_inputs({
        "content": content,
        "deal_id": deal_id,
        "person_id": person_id,
        "org_id": org_id,
        "lead_id": lead_id,
        "user_id": user_id,
    })
    content = sanitized["content"]

    if not content or not content.strip():
        return format_tool_response(False, error_message="The 'content' field is required and cannot be empty.")

    deal_id_int, err = convert_id_string(sanitized["deal_id"], "deal_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    person_id_int, err = convert_id_string(sanitized["person_id"], "person_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    org_id_int, err = convert_id_string(sanitized["org_id"], "org_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    user_id_int, err = convert_id_string(sanitized["user_id"], "user_id", "123")
    if err:
        return format_tool_response(False, error_message=err)
    lead_uuid, err = validate_uuid_string(
        sanitized["lead_id"], "lead_id", "123e4567-e89b-12d3-a456-426614174000"
    )
    if err:
        return format_tool_response(False, error_message=err)

    if all(v is None for v in (deal_id_int, person_id_int, org_id_int, lead_uuid)):
        return format_tool_response(
            False,
            error_message="At least one of deal_id, person_id, org_id, or lead_id must be provided.",
        )

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        note = Note(
            content=content,
            deal_id=deal_id_int,
            person_id=person_id_int,
            org_id=org_id_int,
            lead_id=lead_uuid,
            user_id=user_id_int,
            pinned_to_deal_flag=pinned_to_deal_flag,
            pinned_to_person_flag=pinned_to_person_flag,
            pinned_to_organization_flag=pinned_to_organization_flag,
            pinned_to_lead_flag=pinned_to_lead_flag,
        )
        payload = note.to_create_payload()
        created = await pd_mcp_ctx.pipedrive_client.notes.create_note(**payload)
        logger.info(f"Successfully created note with ID: {created.get('id')}")
        return format_tool_response(True, data=created)
    except ValidationError as e:
        logger.error(f"Validation error creating note: {e}")
        return format_tool_response(False, error_message=f"Validation error: {e}")
    except PipedriveAPIError as e:
        logger.error(f"Pipedrive API error creating note: {e}")
        return format_tool_response(False, error_message=f"Pipedrive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating note: {e}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {e}")
