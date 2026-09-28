"""Integração com OpenAI utilizando o SDK oficial."""

import os
from typing import Dict, List

import openai

from src.providers.base import BaseLLMProvider, LLMError, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        if not self.is_available():
            raise LLMError(self.provider_name, "Variável de ambiente OPENAI_API_KEY não configurada.")

        client = openai.OpenAI(api_key=self.api_key, timeout=30.0)
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = response.choices[0].message.content or ""
            return LLMResponse(content=content, provider=self.provider_name, model=self.model)
        except openai.RateLimitError as exc:
            raise LLMError(self.provider_name, f"Limite de cota excedido ou saldo insuficiente: {exc}", 429) from exc
        except openai.AuthenticationError as exc:
            raise LLMError(self.provider_name, f"Chave de API OpenAI inválida: {exc}", 401) from exc
        except openai.APIConnectionError as exc:
            raise LLMError(self.provider_name, f"Falha de conexão com os servidores da OpenAI: {exc}") from exc
        except openai.APIError as exc:
            raise LLMError(self.provider_name, f"Erro na API da OpenAI: {exc}", getattr(exc, "status_code", None)) from exc
        except Exception as exc:
            raise LLMError(self.provider_name, f"Erro inesperado: {exc}") from exc
