from typing import Optional

from mcp.server.fastmcp import Context

from pipedrive.api.features.custom_fields.tools.deal_fields_list_tool import (
    _list_fields_impl,
)
from pipedrive.api.features.tool_decorator import tool


@tool("custom_fields")
async def list_person_fields_from_pipedrive(
    ctx: Context,
    limit_str: Optional[str] = "100",
    start_str: Optional[str] = "0",
) -> str:
    """Lists person fields (standard and custom) from Pipedrive CRM.

    Returns the field metadata for persons: id, key (the API key used in
    create/update payloads), name, field_type, and the options list for
    enum/set fields. Use this to discover what custom fields are configured
    before creating or updating a person.

    Format requirements:
    - limit_str: Numeric string between 1-500 (default "100")
    - start_str: Numeric offset for pagination (default "0")

    Example:
    ```
    list_person_fields_from_pipedrive(limit_str="200")
    ```

    Args:
        ctx: Context object provided by the MCP server
        limit_str: Maximum number of results (default "100", max "500")
        start_str: Pagination offset (default "0")

    Returns:
        JSON formatted response with the person field list and pagination info, or error message
    """
    return await _list_fields_impl(
        ctx,
        limit_str,
        start_str,
        "list_person_fields_from_pipedrive",
        "list_person_fields",
    )
