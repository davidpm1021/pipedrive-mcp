from pipedrive.api.features.tool_registry import registry, FeatureMetadata
from pipedrive.api.features.users.tools.user_list_tool import list_users_from_pipedrive
from pipedrive.api.features.users.tools.user_get_tool import get_user_from_pipedrive

# Register the feature
registry.register_feature(
    "users",
    FeatureMetadata(
        name="Users",
        description="Read-only tools for inspecting Pipedrive account users",
        version="1.0.0",
    )
)

# Register all tools for this feature
registry.register_tool("users", list_users_from_pipedrive)
registry.register_tool("users", get_user_from_pipedrive)
