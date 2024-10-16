import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from openai import NOT_GIVEN
from openai.resources.chat import AsyncCompletions
from openai.resources.embeddings import AsyncEmbeddings
from pydantic import BaseModel

from src.client_wrapper import AsyncClaude
from src.main import app

client = TestClient(app)
base_data = {"text": "How are you?"}


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


@patch.object(AsyncCompletions, "create", new_callable=AsyncMock, return_value=FakeCompletion)
@patch.object(AsyncClaude, "create", new_callable=AsyncMock, return_value=FakeCompletion)
class TestChatBot(unittest.TestCase):
    def test_message_param(self, _, mock_openai_create: AsyncMock):
        messages = [
            {"role": "system", "content": "You are a chatbot"},
            {"role": "user", "content": "How are you"},
        ]
        resp = client.post(
            "/gpt_openai",
            json=base_data
            | {
                "model": "gpt-3.5-turbo",
                "messages": messages,
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["reply"], FakeCompletion.Choice.message.content)
        mock_openai_create.assert_called_with(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
            seed=None,
            response_format=NOT_GIVEN,
        )

    def test_json_mode(self, _, mock_openai_create: AsyncMock):
        api = "/gpt_openai"
        param = {
            "text": "将一下内容转为json：\nname: John, age: 18",
            "model": "gpt-4o-2024-08-06",
            "service": "openai",
        }

        class Person(BaseModel):
            name: str
            age: int

        prev_content = FakeCompletion.Choice.message.content
        FakeCompletion.Choice.message.content = '{"name": "John", "age": 18}'
        person = Person(name="John", age=18)
        for test_param, expected_response_format in (
            ({"json_mode": True}, {"type": "json_object"}),
            (
                {"json_mode": {"name": "output", "schema": Person.model_json_schema()}},
                {
                    "type": "json_schema",
                    "json_schema": {"name": "output", "schema": Person.model_json_schema()},
                },
            ),
        ):
            with self.subTest(**test_param):
                response = client.post(api, json=param | test_param)
                self.assertEqual(response.status_code, 200)
                result = Person.model_validate_json(response.json()["reply"])
                self.assertEqual(result, person)
                mock_openai_create.assert_called_with(
                    model="gpt-4o-2024-08-06",
                    messages=[{"role": "user", "content": param["text"]}],
                    temperature=0,
                    seed=None,
                    response_format=expected_response_format,
                )

        FakeCompletion.Choice.message.content = prev_content

    def test_service(self, _, __):
        api = "/gpt_openai"
        for model, service in (
            ("gpt-3.5-turbo", "openai"),
            ("gpt35-turbo-16k", "azure"),
            ("deepseek-chat", "dpsk"),
            ("deepseek-chat", "deepseek"),
            ("ep-20240604102539-lz8dk", "doubao"),
            ("claude-3-haiku-20240307", "claude"),
            ("abab6.5s-chat", "minimax"),
            ("moonshot-v1-8k", "moonshot"),
        ):
            param = {"model": model, "service": service}
            with self.subTest(**param):
                response = client.post(api, json=base_data | param)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["reply"], FakeCompletion.Choice.message.content)
                self.assertEqual(data["usage"], FakeCompletion.usage)

    def test_system_message(self, _mock_claude_create, mock_openai_create: AsyncMock):
        api = "/gpt_openai"
        data = {"text": "How are you", "system": "You are a chatbot", "model": "gpt-3.5-turbo"}
        response = client.post(api, json=data)
        self.assertEqual(response.status_code, 200)
        mock_openai_create.assert_called_with(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "How are you"},
            ],
            temperature=0,
            seed=None,
            response_format=NOT_GIVEN,
        )

    @patch.object(AsyncEmbeddings, "create", new_callable=AsyncMock, return_value=FakeEmbedding)
    def test_api(self, mock_embedding_create, mock_claude_create, mock_openai_create):

        embedding_resp = FakeEmbedding.embedding.embedding
        completion_resp = FakeCompletion.Choice.message.content

        for api, data, expected_resp in (
            (
                "/gpt_openai_v2",
                base_data
                | {
                    "model": "gpt35-turbo-16k",
                    "OPENAI_API_KEY": "sk-",
                    "service": "claude",
                },
                completion_resp,
            ),
            ("/get_token_num", base_data, 4),
            ("/vec", base_data, embedding_resp),
            (
                "/vec",
                base_data | {"model": "text-embedding-3-small", "dimensions": 512},
                embedding_resp,
            ),
            ("/vec_openai", base_data, embedding_resp),
            ("/azure_vec", base_data | {"OPENAI_API_KEY": "sk-"}, embedding_resp),
            (
                "/gpt_openai_fast",
                {
                    "prompts": [base_data["text"], base_data["text"]],
                    "model": "claude-3-haiku-20240307",
                    "service": "claude",
                },
                [completion_resp, completion_resp],
            ),
        ):
            with self.subTest(api=api):
                response = client.post(api, json=data)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["reply"], expected_resp)


if __name__ == "__main__":
    unittest.main()
