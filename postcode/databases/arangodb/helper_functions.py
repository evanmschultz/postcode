from typing import Any, Union

from postcode.models.enums import BlockType
from postcode.models.models import (
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
)

# from postcode.types.postcode import ModelType

ModelType = Union[
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
]


def pluralized_and_lowered_block_types() -> list[str]:
    return [pluralize_block_type(block_type).lower() for block_type in BlockType]


def pluralize_block_type(block_type: str) -> str:
    if block_type == BlockType.CLASS:
        return "classes"
    else:
        return f"{block_type.lower()}s"


def create_model_from_vertex(vertex_data: dict) -> ModelType:
    block_type = vertex_data.get("block_type")

    if block_type == BlockType.MODULE:
        return ModuleModel(**vertex_data)
    elif block_type == BlockType.CLASS:
        return ClassModel(**vertex_data)
    elif block_type == BlockType.FUNCTION:
        return FunctionModel(**vertex_data)
    elif block_type == BlockType.STANDALONE_CODE_BLOCK:
        return StandaloneCodeBlockModel(**vertex_data)
    else:
        raise ValueError(f"Unknown block type: {block_type}")