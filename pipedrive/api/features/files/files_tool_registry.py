from pipedrive.api.features.tool_registry import registry, FeatureMetadata
from pipedrive.api.features.files.tools.file_list_tool import list_files_from_pipedrive
from pipedrive.api.features.files.tools.file_get_tool import get_file_metadata_from_pipedrive

# Register the feature
registry.register_feature(
    "files",
    FeatureMetadata(
        name="Files",
        description="Read-only tools for inspecting file metadata attached to Pipedrive entities",
        version="1.0.0",
    )
)

# Register all tools for this feature
registry.register_tool("files", list_files_from_pipedrive)
registry.register_tool("files", get_file_metadata_from_pipedrive)
