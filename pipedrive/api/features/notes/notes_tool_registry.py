from pipedrive.api.features.tool_registry import registry, FeatureMetadata
from pipedrive.api.features.notes.tools.note_create_tool import create_note_in_pipedrive
from pipedrive.api.features.notes.tools.note_get_tool import get_note_from_pipedrive
from pipedrive.api.features.notes.tools.note_update_tool import update_note_in_pipedrive
from pipedrive.api.features.notes.tools.note_list_tool import list_notes_from_pipedrive

# Register the feature
registry.register_feature(
    "notes",
    FeatureMetadata(
        name="Notes",
        description="Tools for managing notes attached to deals, persons, organizations, and leads",
        version="1.0.0",
    )
)

# Register all tools for this feature
registry.register_tool("notes", create_note_in_pipedrive)
registry.register_tool("notes", get_note_from_pipedrive)
registry.register_tool("notes", update_note_in_pipedrive)
registry.register_tool("notes", list_notes_from_pipedrive)
