from fastapi import APIRouter, Body
from pydantic import BaseModel, Field

from src.ark_sign import ark_model_list
from src.clients import CLIENTS
from src.schema import ServiceProvider

router = APIRouter(tags=["模型列表"], prefix="/models")


class ModelInfo(BaseModel):
    id: str = Field(description="模型调用ID")
    model: str = Field("", description="模型名称")


ModelList: dict[ServiceProvider, list[ModelInfo]] = {
    "dpsk": [
        ModelInfo(id="deepseek-chat", model="deepseek-chat"),
        ModelInfo(id="deepseek-coder", model="deepseek-coder"),
    ],
    "azure": [
        ModelInfo(id="gpt4-0125-preview", model="gpt-4"),
        ModelInfo(id="gpt-4-0125-preview", model="gpt-4"),
        ModelInfo(id="gpt35-turbo-16k", model="gpt-35-turbo-16k"),
        ModelInfo(id="text-embedding-3-large", model="text-embedding-3-large"),
        ModelInfo(id="text-embedding-3-small", model="text-embedding-3-small"),
        ModelInfo(id="text-embedding-ada-002", model="text-embedding-ada-002"),
    ],
    "claude": [
        ModelInfo(id="claude-3-5-sonnet-20240620", model="claude-3-5-sonnet"),
        ModelInfo(id="claude-3-opus-20240229", model="claude-3-opus"),
        ModelInfo(id="claude-3-sonnet-20240229", model="claude-3-sonnet"),
        ModelInfo(id="claude-3-haiku-20240307", model="claude-3-haiku"),
    ],
    "minimax": [
        ModelInfo(id="abab5.5-chat", model="abab5.5"),
        ModelInfo(id="abab5.5s-chat", model="abab5.5s"),
        ModelInfo(id="abab6.5t-chat", model="abab6.5t"),
        ModelInfo(id="abab6.5g-chat", model="abab6.5g"),
        ModelInfo(id="abab6.5s-chat", model="abab6.5s"),
    ],
}


@router.post("/list", summary="获取各服务商可用的模型列表", response_model=list[ModelInfo])
async def model_list(service: ServiceProvider = Body(embed=True)):
    if service in ("openai", "moonshot"):
        return (await CLIENTS[service].models.list()).data
    elif service == "doubao":
        models = await ark_model_list()
        return [
            {
                "id": model["Id"],
                "model": f"{model['ModelReference']['FoundationModel']['Name']}/"
                f"{model['ModelReference']['FoundationModel']['ModelVersion']}",
            }
            for model in models
        ]
    return ModelList[service]
