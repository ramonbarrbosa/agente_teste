"""Integração com OpenRouter utilizando o SDK oficial da OpenAI."""

import os
from typing import Dict, List

import openai

from src.providers.base import BaseLLMProvider, LLMError, LLMResponse


class OpenRouterProvider(BaseLLMProvider):
    def __init__(self, model: str = "google/gemma-4-31b-it:free"):
        self.model = model
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

    @property
    def provider_name(self) -> str:
        return "OpenRouter"

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
            raise LLMError(self.provider_name, "Variável de ambiente OPENROUTER_API_KEY não configurada.")

        client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=30.0,
            default_headers={
                "HTTP-Referer": "https://huggingface.co/spaces/ramonbarrbosa/agente-teste",
                "X-Title": "Prof. Ada",
            },
        )

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
            raise LLMError(self.provider_name, f"Limite de requisições ou créditos esgotados: {exc}", 429) from exc
        except openai.AuthenticationError as exc:
            raise LLMError(self.provider_name, f"Chave de API inválida ou expirada: {exc}", 401) from exc
        except openai.APIConnectionError as exc:
            raise LLMError(self.provider_name, f"Falha de conexão com os servidores do OpenRouter: {exc}") from exc
        except openai.APIError as exc:
            raise LLMError(self.provider_name, f"Erro na API do OpenRouter: {exc}", getattr(exc, "status_code", None)) from exc
        except Exception as exc:
            raise LLMError(self.provider_name, f"Erro inesperado: {exc}") from exc
