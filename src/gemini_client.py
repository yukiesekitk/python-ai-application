import time

import streamlit as st
from google import genai
from google.genai import errors, types

_MAX_RETRIES = 3
_RETRY_BACKOFF_SECONDS = 2
_RETRYABLE_CLIENT_CODES = (429,)


@st.cache_resource
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def generate(
    client: genai.Client,
    model: str,
    prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.8,
) -> str:
    """Gemini APIにプロンプトを送り、生成されたテキストを返す。

    503（サーバー混雑）や429（レート制限）のような一時的なエラーは、
    待機を挟んで自動的に数回リトライする。404など恒久的なエラーは即座に上に投げる。
    """
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
    )
    last_error: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            return (response.text or "").strip()
        except errors.ServerError as e:
            last_error = e
        except errors.ClientError as e:
            if e.code not in _RETRYABLE_CLIENT_CODES:
                raise
            last_error = e

        if attempt < _MAX_RETRIES - 1:
            time.sleep(_RETRY_BACKOFF_SECONDS * (attempt + 1))

    raise last_error
