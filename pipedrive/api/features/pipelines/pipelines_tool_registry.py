from pipedrive.api.features.tool_registry import registry, FeatureMetadata
from pipedrive.api.features.pipelines.tools.pipeline_list_tool import list_pipelines_from_pipedrive
from pipedrive.api.features.pipelines.tools.pipeline_get_tool import get_pipeline_from_pipedrive
from pipedrive.api.features.pipelines.tools.stage_list_tool import list_stages_from_pipedrive
from pipedrive.api.features.pipelines.tools.stage_get_tool import get_stage_from_pipedrive
from pipedrive.api.features.pipelines.tools.pipeline_deals_list_tool import list_deals_in_pipeline_from_pipedrive

# Register the feature
registry.register_feature(
    "pipelines",
    FeatureMetadata(
        name="Pipelines and Stages",
        description="Read-only tools for inspecting pipelines, stages, and deals within a pipeline",
        version="1.0.0",
    )
)

# Register all tools for this feature
registry.register_tool("pipelines", list_pipelines_from_pipedrive)
registry.register_tool("pipelines", get_pipeline_from_pipedrive)
registry.register_tool("pipelines", list_stages_from_pipedrive)
registry.register_tool("pipelines", get_stage_from_pipedrive)
registry.register_tool("pipelines", list_deals_in_pipeline_from_pipedrive)
