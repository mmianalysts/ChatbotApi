import logging
import traceback

from fastapi import APIRouter, Request

from src.retrieve_text import (
    azure,
    chatbot_gpt4,
    chatbot_gpt4_turbo,
    chatbot_openai,
    chatbot_openai_hispreadnlp,
)

router = APIRouter(tags=["Deprecated APIs"])


@router.post("/chatbot", deprecated=True)
async def bot_helper_http(req: Request):
    print("In fastapi_helper: bot_helper_http")
    try:
        body = await req.json()
        print(body)
        data = body
        try:
            human_input = data["text"]
            data["reply"] = await chatbot_openai(human_input, "gpt-3.5-turbo", "openai")
            data["status"] = "ok"
        except Exception:
            print("In fastapi_ws.py, bot_helper_http error occurred")
            traceback.print_exc()
            data["reply"] = ""
            data["status"] = "error"

        logging.info("Input: %s\n\tReply: %s\n", data["text"], data["reply"])
    except Exception:
        print("error")
        traceback.print_exc()
        data = {}

    return data


@router.post("/gpt4", deprecated=True)
async def bot2_helper_http(req: Request):
    print("In fastapi_helper: bot_helper_http")
    print("start gpt4!")
    try:
        body = await req.json()
        print(body)
        data = body
        try:
            human_input = data["text"]
            data["reply"] = await chatbot_gpt4(human_input)
            data["status"] = "ok"
            print("调用了gpt接口")
        except Exception:
            print("In fastapi_ws.py, bot_helper_http error occurred")
            traceback.print_exc()
            data["reply"] = ""
            data["status"] = "error"

        logging.info("Input: %s\n\tReply: %s\n", data["text"], data["reply"])
    except Exception:
        print("error")
        traceback.print_exc()
        data = {}

    return data


@router.post("/gpt4_turbo", deprecated=True)
async def bot3_helper_http_gpt4_turbo(req: Request):
    print("In fastapi_helper: bot_helper_http")
    print("start gpt4t!")
    try:
        body = await req.json()
        print(body)
        data = body
        try:
            human_input = data["text"]
            data["reply"] = await chatbot_gpt4_turbo(human_input)
            data["status"] = "ok"
            print("调用了gpt4t接口")
        except Exception:
            print("In fastapi_ws.py, bot_helper_http error occurred")
            traceback.print_exc()
            data["reply"] = ""
            data["status"] = "error"

        logging.info("Input: %s\n\tReply: %s\n", data["text"], data["reply"])
    except Exception:
        print("error")
        traceback.print_exc()
        data = {}

    return data


@router.post("/gpt_openai2", deprecated=True)
async def bot6_helper_http(req: Request):
    print("In fastapi_helper: bot_helper_http")
    print("start gpt4t!")
    data = {}
    try:
        body = await req.json()
        print(body)
        data = body
        try:
            human_input = data["text"]
            data["reply"] = await chatbot_openai_hispreadnlp(human_input, data["model"])
            data["status"] = "ok"
            print("调用了gpt4t接口")
        except Exception:
            print("In fastapi_ws.py, bot_helper_http error occurred")
            traceback.print_exc()
            data["reply"] = ""
            data["status"] = "error"

        logging.info("Input: %s\n\tReply: %s\n", data["text"], data["reply"])
    except Exception:
        print("error")
        traceback.print_exc()
        data["reply"] = ""
        data["status"] = "error"

    logging.info("Input: %s\n\tReply: %s\n", data["text"], data["reply"])

    return data


@router.post("/azure", deprecated=True)
async def bot3_helper_http(req: Request):
    print("In fastapi_helper: bot_helper_http")
    data = {}
    try:
        body = await req.json()
        print(body)
        data = body
        try:
            data["reply"] = await azure(data["text"])
            data["status"] = "ok"
        except Exception:
            print("In fastapi_ws.py, bot_helper_http error occurred")
            traceback.print_exc()
            data["reply"] = ""
            data["status"] = "error"

        logging.info("Input: %s\n\tReply: %s\n", data["text"], data["reply"])
    except Exception:
        print("error")
        traceback.print_exc()

    return data
