from typing import Optional, Union

from openai import NOT_GIVEN
from openai.types.chat import ChatCompletionMessageParam

from src.clients import CLIENTS
from src.schema import ResponseFormat, ServiceProvider
from src.utils import log_completion_info


async def chatbot_gpt4(text):
    response = await CLIENTS["openai"].chat.completions.create(
        model="gpt-4", messages=[{"role": "user", "content": text}], timeout=6000
    )
    contents = response.choices[0].message.content
    assert contents, response
    print(f"{response=}")
    return contents


async def chatbot_gpt4_turbo(text):
    response = await CLIENTS["openai"].chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": text}],
        timeout=6000,
    )
    contents = response.choices[0].message.content
    assert contents, response
    print("gpt-4-turbo", response)
    return contents


@log_completion_info("messages", "model", "service", "info")
async def chatbot_openai(
    messages: list[ChatCompletionMessageParam],
    model: str,
    service: ServiceProvider,
    temperature: Optional[float] = None,
    seed: Optional[int] = None,
    response_format: ResponseFormat = NOT_GIVEN,
    **extra_params,
):
    extra_params.pop("info", None)  # 'info'不需要传递给create函数，仅用作日志记录
    response = await CLIENTS[service].chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        seed=seed,
        response_format=response_format,
        **extra_params,
    )
    contents = response.choices[0].message.content
    assert contents, response
    return contents, response.usage


async def chatbot_openai_hispreadnlp(text, model):
    response = await CLIENTS["openai"].chat.completions.create(
        model=model, messages=[{"role": "user", "content": text}], timeout=6000
    )
    contents = response.choices[0].message.content
    print("gpt-openai_hispreadnlp", response)
    assert contents, response
    return contents


async def vec(
    words_list: Union[str, list[str]],
    service: ServiceProvider,
    model: str,
    dimensions: Optional[int],
) -> Union[list[float], list[list[float]]]:
    if service not in ("openai", "azure"):
        raise Exception(f"服务{service}不可用")
    assert model != "text-embedding-ada-002" or dimensions is None, "ada不支持dimensions"
    kwargs = {"model": model, "input": words_list}
    if dimensions:
        kwargs["dimensions"] = dimensions

    client = CLIENTS[service]
    res = await client.embeddings.create(**kwargs)
    embeddings = [embedding.embedding for embedding in res.data]
    if isinstance(words_list, str):
        embeddings = embeddings[0]
    return embeddings


async def azure(text):
    response = await CLIENTS["openai"].chat.completions.create(
        model="gpt-services",
        messages=[{"role": "user", "content": "%s" % text}],
        temperature=0,
        max_tokens=2000,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    return response.choices[0].message.content
