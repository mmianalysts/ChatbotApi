"""
火山云鉴权签名示例，Refer: https://github.com/volcengine/volc-openapi-demos/blob/main/signature/python/sign.py
"""

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Literal, Optional, Union
from urllib.parse import quote

import httpx

# 以下参数视服务不同而不同，一个服务内通常是一致的
SERVICE = "ark"
REGION = "cn-beijing"
HOST = "open.volcengineapi.com"

# 火山云请求的凭证 https://console.volcengine.com/iam/keymanage
AK = os.getenv("VOLC_ACCESSKEY", "")
SK = os.getenv("VOLC_SECRETKEY", "")
assert AK, "Please set VOLC_ACCESSKEY"
assert SK, "Please set VOLC_SECRETKEY"


def norm_query(params: dict[str, Union[str, list[str]]]) -> str:
    return "&".join(
        [
            f"{quote(k, safe='-_.~')}={quote(i, safe='-_.~')}"
            for k, v in sorted(params.items())
            for i in (v if isinstance(v, list) else [v])
        ]
    ).replace("+", "%20")


# sha256 非对称加密
def hmac_sha256(key: bytes, content: str):
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


# sha256 hash算法
def hash_sha256(content: str):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def sign_header(
    method: Literal["POST"],
    path: str,
    query: Optional[dict] = None,
    data: Optional[dict] = None,
) -> dict[str, str]:
    now = datetime.now(timezone.utc)
    x_date = now.strftime("%Y%m%dT%H%M%SZ")
    short_x_date = now.strftime("%Y%m%d")
    x_content_sha256 = hash_sha256(json.dumps(data) if data else "")

    # 签名的表头
    signed_headers_str = ";".join(["host", "x-content-sha256", "x-date"])
    # 规范请求字符串
    canonical_request_str = "\n".join(
        [
            method,
            path,
            norm_query(query or {}),
            "\n".join(
                [
                    "host:" + HOST,
                    "x-content-sha256:" + x_content_sha256,
                    "x-date:" + x_date,
                ]
            ),
            "",
            signed_headers_str,
            x_content_sha256,
        ]
    )
    hashed_canonical_request = hash_sha256(canonical_request_str)

    # 生成签名字符串
    credential_scope = "/".join([short_x_date, REGION, SERVICE, "request"])
    string_to_sign = "\n".join(["HMAC-SHA256", x_date, credential_scope, hashed_canonical_request])

    # 生成签名
    k_date = hmac_sha256(SK.encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, REGION)
    k_service = hmac_sha256(k_region, SERVICE)
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()

    return {
        "Host": HOST,
        "X-Date": x_date,
        "X-Content-Sha256": x_content_sha256,
        "Authorization": f"HMAC-SHA256 Credential={AK}/{credential_scope}, "
        f"SignedHeaders={signed_headers_str}, "
        f"Signature={signature}",
    }


async def ark_model_list() -> dict:
    query = {"Action": "ListEndpoints", "PageSize": "100", "Version": "2024-01-01"}
    data = {"Filter": {"Statuses": ["Running"]}}
    signed = sign_header("POST", "/", query, data)
    async with httpx.AsyncClient() as client:
        res = await client.post(f"https://{HOST}", headers=signed, params=query, json=data)
        return res.json()["Result"]["Items"]


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(ark_model_list()))
