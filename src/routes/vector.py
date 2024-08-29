from typing import Literal, Optional, Union

from fastapi import APIRouter, Body
from pydantic import BaseModel

from src.retrieve_text import vec
from src.schema import ServiceProvider

router = APIRouter(tags=["向量化"])

VectorModel = Literal[
    "text-embedding-ada-002",
    "text-embedding-3-small",
    "text-embedding-3-large",
]


class VectorReq(BaseModel):
    text: Union[str, list[str]] = Body(description="需要向量化的文本")
    model: VectorModel = Body(
        default="text-embedding-ada-002", description="向量化模型, 可用性取决于具体服务商"
    )
    service: ServiceProvider = Body(default="openai", description="LLM服务供应商")
    dimensions: Optional[int] = Body(default=None, description="向量维度")


@router.post("/vec", deprecated=True)
@router.post("/vec_openai", description="文本转向量")
async def text_vector(body: VectorReq):
    print("In fastapi_helper: bot_helper_http")
    data = body.model_dump()
    data["reply"] = await vec(body.text, body.service, body.model, body.dimensions)
    data["status"] = "ok"
    return data


@router.post("/azure_vec", deprecated=True)
async def vec_azure(text: str = Body(embed=True)):
    return await text_vector(VectorReq(text=text, service="azure"))
