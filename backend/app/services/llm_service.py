"""LLM provider abstraction. Supports "anthropic" and "groq"."""

import logging
from typing import NoReturn, Protocol

import httpx

from app.core.config import Settings
from app.core.exceptions import LLMError
from app.models.conversation import Message
from app.rag.prompt import SYSTEM_PROMPT, build_user_message

logger = logging.getLogger("evidencerag")

_MAX_ANSWER_TOKENS = 1024
_GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_REQUEST_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)


class _Provider(Protocol):
    def generate(self, question: str, context: str, history: list[Message]) -> str: ...


class _AnthropicProvider:
    def __init__(self, settings: Settings) -> None:
        import anthropic

        # api_key=None lets the SDK resolve credentials from the environment
        # (ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / an `ant auth login` profile).
        self._client = anthropic.Anthropic(api_key=settings.llm_api_key or None)
        self._model = settings.llm_model

    def generate(self, question: str, context: str, history: list[Message]) -> str:
        messages = [
            {"role": message.role, "content": message.content} for message in history
        ]
        messages.append({"role": "user", "content": build_user_message(question, context)})

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=_MAX_ANSWER_TOKENS,
                system=SYSTEM_PROMPT,
                messages=messages,
                output_config={"effort": "low"},
            )
        except Exception as exc:
            self._raise_llm_error(exc)

        for block in response.content:
            if block.type == "text":
                return block.text

        raise LLMError("The AI service returned an unexpected response.")

    def _raise_llm_error(self, exc: Exception) -> NoReturn:
        import anthropic

        if isinstance(exc, anthropic.AuthenticationError):
            logger.error("llm_authentication_failed")
            raise LLMError("The AI service is not configured correctly.") from exc
        if isinstance(exc, anthropic.RateLimitError):
            logger.warning("llm_rate_limited")
            raise LLMError("The AI service is currently rate-limited. Please try again.") from exc
        if isinstance(exc, anthropic.APITimeoutError):
            logger.error("llm_timeout")
            raise LLMError("The AI service timed out. Please try again.") from exc
        if isinstance(exc, anthropic.APIConnectionError):
            logger.error("llm_connection_error")
            raise LLMError("Could not reach the AI service.") from exc
        if isinstance(exc, anthropic.APIStatusError):
            logger.error("llm_api_error", extra={"status_code": exc.status_code})
            raise LLMError("The AI service is currently unavailable.") from exc

        logger.exception("llm_unexpected_error")
        raise LLMError("The AI service is currently unavailable.") from exc


class _GroqProvider:
    """Calls Groq's OpenAI-compatible chat-completions endpoint directly via httpx."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.llm_api_key
        self._model = settings.llm_model

    def generate(self, question: str, context: str, history: list[Message]) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(
            {"role": message.role, "content": message.content} for message in history
        )
        messages.append({"role": "user", "content": build_user_message(question, context)})

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": _MAX_ANSWER_TOKENS,
        }

        try:
            response = httpx.post(
                _GROQ_CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
                timeout=_GROQ_REQUEST_TIMEOUT,
            )
        except httpx.TimeoutException as exc:
            logger.error("llm_timeout")
            raise LLMError("The AI service timed out. Please try again.") from exc
        except httpx.RequestError as exc:
            logger.error("llm_connection_error")
            raise LLMError("Could not reach the AI service.") from exc

        if response.status_code == 401 or response.status_code == 403:
            logger.error("llm_authentication_failed")
            raise LLMError("The AI service is not configured correctly.")
        if response.status_code == 429:
            logger.warning("llm_rate_limited")
            raise LLMError("The AI service is currently rate-limited. Please try again.")
        if response.status_code >= 400:
            logger.error("llm_api_error", extra={"status_code": response.status_code})
            raise LLMError("The AI service is currently unavailable.")

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            logger.exception("llm_unexpected_error")
            raise LLMError("The AI service returned an unexpected response.") from exc


_PROVIDERS: dict[str, type[_Provider]] = {
    "anthropic": _AnthropicProvider,
    "groq": _GroqProvider,
}


class LLMService:
    def __init__(self, settings: Settings) -> None:
        provider_cls = _PROVIDERS.get(settings.llm_provider)
        if provider_cls is None:
            raise ValueError(
                f"Unsupported LLM provider: '{settings.llm_provider}'. "
                f"Supported providers: {', '.join(sorted(_PROVIDERS))}."
            )
        self._provider: _Provider = provider_cls(settings)

    def generate(self, question: str, context: str, history: list[Message]) -> str:
        return self._provider.generate(question, context, history)
