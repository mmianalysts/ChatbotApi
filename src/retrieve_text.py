from typing import Optional, Union

from src.clients import CLIENTS
from src.schema import ServiceProvider


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
        model="gpt-4-1106-preview", messages=[{"role": "user", "content": text}], timeout=6000
    )
    contents = response.choices[0].message.content
    assert contents, response
    print("gpt-4-turbo", response)
    return contents


async def chatbot_openai(
    text: str,
    model: str,
    service: ServiceProvider,
    pic: Optional[str] = None,
    temperature: float = 1,
):
    client = CLIENTS[service]
    content = text
    if pic:
        if not pic.startswith("http"):
            pic = "data:image/jpeg;base64," + pic
        content = [{"type": "text", "text": text}, {"type": "image_url", "image_url": {"url": pic}}]
    messages = [{"role": "user", "content": content}]

    response = await client.chat.completions.create(
        model=model, messages=messages, temperature=temperature  # type: ignore
    )
    contents = response.choices[0].message.content
    assert contents, response
    return contents


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


if __name__ == "__main__":
    import asyncio

    a = asyncio.run(chatbot_openai("1+1", "gpt-3.5-turbo", "openai"))
    print(a)
