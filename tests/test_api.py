import unittest

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestChatBot(unittest.TestCase):
    def test_service(self):
        api = "/gpt_openai"
        data = {"text": "How are you"}
        for model, service in (
            ("gpt-3.5-turbo", "openai"),
            ("gpt35-turbo-16k", "azure"),
            ("deepseek-chat", "dpsk"),
            ("ep-20240604102539-lz8dk", "doubao"),
            ("claude-3-haiku-20240307", "claude"),
            ("abab6.5s-chat", "minimax"),
        ):
            param = {"model": model, "service": service}
            with self.subTest(**param):
                response = client.post(api, json=data | param)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["reply"])

    def test_api(self):
        for api, data in (
            (
                "/gpt_openai_v2",
                {
                    "text": "How are you?",
                    "model": "gpt35-turbo-16k",
                    "OPENAI_API_KEY": "sk-",
                    "service": "claude",
                },
            ),
            ("/get_token_num", {"text": "How are you?"}),
            ("/vec", {"text": "How are you?"}),
            (
                "/vec",
                {"text": "How are you?", "model": "text-embedding-3-small", "dimensions": 512},
            ),
            ("/vec_openai", {"text": "How are you?"}),
            ("/azure_vec", {"text": "How are you?", "OPENAI_API_KEY": "sk-"}),
            (
                "/gpt_openai_fast",
                {
                    "prompts": ["How are you?"],
                    "model": "claude-3-haiku-20240307",
                    "service": "claude",
                },
            ),
        ):
            with self.subTest(api=api):
                response = client.post(api, json=data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["reply"])


if __name__ == "__main__":
    unittest.main()
