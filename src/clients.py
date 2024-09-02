import os

from httpx import AsyncClient
from openai import AsyncAzureOpenAI, AsyncOpenAI

from src.client_wrapper import AsyncClaude
from src.schema import ServiceProvider

# openai and azure auto load api_key from environment variable: OPENAI_API_KEY, AZURE_OPENAI_API_KEY
proxy_client = AsyncClient(
    proxy=f"http://{os.environ['SG_PROXY_USER']}:{os.environ['SG_PROXY_PASSWD']}"
    "@agent-proxy:24869"
)
OPENAI_CLIENT = AsyncOpenAI(http_client=proxy_client)
AZURE_CLIENT = AsyncAzureOpenAI(
    azure_endpoint="https://azure-agent1.openai.azure.com/",
    api_version="2023-07-01-preview",
)

DEEP_SEEK_API_KEY = os.getenv("DPSK_API_KEY")
assert DEEP_SEEK_API_KEY is not None, "Please set the environment variable DPSK_API_KEY"
DPSK_CLIENT = AsyncOpenAI(api_key=DEEP_SEEK_API_KEY, base_url="https://api.deepseek.com/")


ARK_API_KEY = os.getenv("ARK_API_KEY")
assert ARK_API_KEY is not None, "Please set the environment variable ARK_API_KEY"
DOUBAO_CLIENT = AsyncOpenAI(
    api_key=ARK_API_KEY, base_url="https://ark.cn-beijing.volces.com/api/v3"
)

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
assert CLAUDE_API_KEY is not None, "Please set the environment variable CLAUDE_API_KEY"
CLAUDE_CLIENT = AsyncClaude(api_key=CLAUDE_API_KEY, http_client=proxy_client)

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
assert MINIMAX_API_KEY is not None, "Please set the environment variable MINI_MAX_API_KEY"
MINIMAX_CLIENT = AsyncOpenAI(api_key=MINIMAX_API_KEY, base_url="https://api.minimax.chat/v1")

CLIENTS: dict[ServiceProvider, AsyncOpenAI] = {
    "openai": OPENAI_CLIENT,
    "azure": AZURE_CLIENT,
    "dpsk": DPSK_CLIENT,
    "doubao": DOUBAO_CLIENT,
    "claude": CLAUDE_CLIENT,
    "minimax": MINIMAX_CLIENT,
}
