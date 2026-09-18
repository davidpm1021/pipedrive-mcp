from pipedrive.api.features.tool_registry import registry, FeatureMetadata
from pipedrive.api.features.filters.tools.filter_list_tool import list_filters_from_pipedrive

# Register the feature
registry.register_feature(
    "filters",
    FeatureMetadata(
        name="Filters",
        description="Read-only tool for discovering saved Pipedrive filters",
        version="1.0.0",
    )
)

# Register all tools for this feature
registry.register_tool("filters", list_filters_from_pipedrive)
