from pipedrive.api.features.tool_registry import registry, FeatureMetadata
from pipedrive.api.features.custom_fields.tools.deal_fields_list_tool import list_deal_fields_from_pipedrive
from pipedrive.api.features.custom_fields.tools.person_fields_list_tool import list_person_fields_from_pipedrive
from pipedrive.api.features.custom_fields.tools.org_fields_list_tool import list_org_fields_from_pipedrive
from pipedrive.api.features.custom_fields.tools.lead_fields_list_tool import list_lead_fields_from_pipedrive

# Register the feature
registry.register_feature(
    "custom_fields",
    FeatureMetadata(
        name="Custom Fields",
        description="Read-only tools for discovering custom and standard fields on deals, persons, and organizations",
        version="1.0.0",
    )
)

# Register all tools for this feature
registry.register_tool("custom_fields", list_deal_fields_from_pipedrive)
registry.register_tool("custom_fields", list_person_fields_from_pipedrive)
registry.register_tool("custom_fields", list_org_fields_from_pipedrive)
registry.register_tool("custom_fields", list_lead_fields_from_pipedrive)
