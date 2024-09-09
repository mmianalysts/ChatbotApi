import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from openai.resources.chat import AsyncCompletions
from openai.resources.embeddings import AsyncEmbeddings

from src.client_wrapper import AsyncClaude
from src.main import app

client = TestClient(app)


class FakeCompletion:
    class Choice:
        class message:
            content = "Fake completion response"

    choices = [Choice]
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


class FakeEmbedding:
    class embedding:
        embedding = [1] * 512

    data = [embedding]


@patch.object(AsyncCompletions, "create", new_callable=AsyncMock)
@patch.object(AsyncClaude, "create", new_callable=AsyncMock)
class TestChatBot(unittest.TestCase):
    def test_service(self, mock_openai_create, mock_claude_create):
        mock_openai_create.return_value = FakeCompletion
        mock_claude_create.return_value = FakeCompletion

        api = "/gpt_openai"
        data = {"text": "How are you"}
        for model, service in (
            ("gpt-3.5-turbo", "openai"),
            ("gpt35-turbo-16k", "azure"),
            ("deepseek-chat", "dpsk"),
            ("ep-20240604102539-lz8dk", "doubao"),
            ("claude-3-haiku-20240307", "claude"),
            ("abab6.5s-chat", "minimax"),
            ("moonshot-v1-8k", "moonshot"),
        ):
            param = {"model": model, "service": service}
            with self.subTest(**param):
                response = client.post(api, json=data | param)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["reply"], FakeCompletion.Choice.message.content)
                self.assertEqual(data["usage"], FakeCompletion.usage)

    @patch.object(AsyncEmbeddings, "create", new_callable=AsyncMock)
    def test_api(self, mock_embedding_create, mock_openai_create, mock_claude_create):
        mock_embedding_create.return_value = FakeEmbedding
        mock_openai_create.return_value = FakeCompletion
        mock_claude_create.return_value = FakeCompletion

        embedding_resp = FakeEmbedding.embedding.embedding
        completion_resp = FakeCompletion.Choice.message.content
        token_num_resp = 3

        for api, data, expected_resp in (
            (
                "/gpt_openai_v2",
                {
                    "text": "How are you?",
                    "model": "gpt35-turbo-16k",
                    "OPENAI_API_KEY": "sk-",
                    "service": "claude",
                },
                completion_resp,
            ),
            ("/get_token_num", {"text": "How are you?"}, token_num_resp),
            ("/vec", {"text": "How are you?"}, embedding_resp),
            (
                "/vec",
                {"text": "How are you?", "model": "text-embedding-3-small", "dimensions": 512},
                embedding_resp,
            ),
            ("/vec_openai", {"text": "How are you?"}, embedding_resp),
            ("/azure_vec", {"text": "How are you?", "OPENAI_API_KEY": "sk-"}, embedding_resp),
            (
                "/gpt_openai_fast",
                {
                    "prompts": ["How are you?"],
                    "model": "claude-3-haiku-20240307",
                    "service": "claude",
                },
                [completion_resp],
            ),
        ):
            with self.subTest(api=api):
                response = client.post(api, json=data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["reply"], expected_resp)


if __name__ == "__main__":
    unittest.main()
