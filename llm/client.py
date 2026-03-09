from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import httpx

from utils.logger import logger
from llm.prompt import DEFAULT_SYSTEM_PROMPT, build_quiz_prompt


@dataclass
class ClaudeConfig:
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 300
    temperature: float = 0.1
    timeout: float = 10.0
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


@dataclass
class OllamaConfig:
    model: str = "qwen2.5:7b"
    timeout: float = 30.0
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
OLLAMA_API_URL = "http://localhost:11434/api/chat"


class ClaudeClientError(RuntimeError):
    pass


class OllamaClientError(RuntimeError):
    pass


def _get_api_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ClaudeClientError(
            "Environment variable ANTHROPIC_API_KEY is not set."
        )
    return key


def ask_claude_for_quiz(
    ocr_text: str,
    config: Optional[ClaudeConfig] = None,
) -> str:
    """
    Отправляет распознанный текст вопроса в Claude и возвращает текстовый ответ.
    Использует HTTP-запрос к Anthropic Messages API.
    """
    if config is None:
        config = ClaudeConfig()

    api_key = _get_api_key()
    user_prompt = build_quiz_prompt(ocr_text)

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": config.model,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "system": config.system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": user_prompt}],
            }
        ],
    }

    logger.info("Sending request to Claude model='{}'", config.model)

    try:
        response = httpx.post(
            ANTHROPIC_API_URL,
            headers=headers,
            json=payload,
            timeout=config.timeout,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("HTTP error while talking to Claude: {}", exc)
        raise ClaudeClientError(f"HTTP error: {exc}") from exc

    if response.status_code != 200:
        logger.error(
            "Claude API returned non-200 status: {} body={}",
            response.status_code,
            response.text,
        )
        raise ClaudeClientError(
            f"Claude API error {response.status_code}: {response.text}"
        )

    data = response.json()
    contents = data.get("content") or []
    text_parts = []
    for block in contents:
        if isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(block.get("text", ""))

    answer_text = "\n".join(t for t in text_parts if t).strip()
    logger.info("Received answer from Claude ({} chars)", len(answer_text))
    return answer_text


def ask_ollama_for_quiz(
    ocr_text: str,
    config: Optional[OllamaConfig] = None,
) -> str:
    """
    Отправляет распознанный текст вопроса в локальную модель Ollama
    (работает без оплаты, но требует установленного Ollama и загруженной модели).
    """
    if config is None:
        config = OllamaConfig()

    user_prompt = build_quiz_prompt(ocr_text)

    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": config.system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }

    logger.info("Sending request to Ollama model='{}'", config.model)

    try:
        response = httpx.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=config.timeout,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("HTTP error while talking to Ollama: {}", exc)
        raise OllamaClientError(f"HTTP error: {exc}") from exc

    if response.status_code != 200:
        logger.error(
            "Ollama API returned non-200 status: {} body={}",
            response.status_code,
            response.text,
        )
        raise OllamaClientError(
            f"Ollama API error {response.status_code}: {response.text}"
        )

    data = response.json()
    message = data.get("message") or {}
    answer_text = (message.get("content") or "").strip()
    logger.info("Received answer from Ollama ({} chars)", len(answer_text))
    return answer_text


__all__ = [
    "ClaudeConfig",
    "ClaudeClientError",
    "ask_claude_for_quiz",
    "OllamaConfig",
    "OllamaClientError",
    "ask_ollama_for_quiz",
]

