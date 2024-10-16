from typing import Literal, Union

from openai import NotGiven
from openai.types.shared_params.response_format_json_object import ResponseFormatJSONObject
from openai.types.shared_params.response_format_json_schema import ResponseFormatJSONSchema

ServiceProvider = Literal[
    "openai", "azure", "dpsk", "deepseek", "doubao", "claude", "minimax", "moonshot"
]
ResponseFormat = Union[ResponseFormatJSONObject, ResponseFormatJSONSchema, NotGiven]
