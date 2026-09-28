"""Integração com Anthropic utilizando o SDK oficial."""

import os
from typing import Dict, List

import anthropic

from src.providers.base import BaseLLMProvider, LLMError, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model: str = "claude-3-5-haiku-latest"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

    @property
    def provider_name(self) -> str:
        return "Anthropic"

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
            raise LLMError(self.provider_name, "Variável de ambiente ANTHROPIC_API_KEY não configurada.")

        client = anthropic.Anthropic(api_key=self.api_key, timeout=30.0)

        # O Anthropic SDK espera 'system' separado e mensagens contendo apenas 'user' e 'assistant'
        clean_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in {"user", "assistant"}
        ]

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=clean_messages,
            )
            # Extrai texto do bloco de resposta
            content_blocks = [b.text for b in response.content if hasattr(b, "text")]
            content = "".join(content_blocks)
            return LLMResponse(content=content, provider=self.provider_name, model=self.model)
        except anthropic.RateLimitError as exc:
            raise LLMError(self.provider_name, f"Limite de requisições excedido: {exc}", 429) from exc
        except anthropic.AuthenticationError as exc:
            raise LLMError(self.provider_name, f"Chave de API Anthropic inválida: {exc}", 401) from exc
        except anthropic.APIConnectionError as exc:
            raise LLMError(self.provider_name, f"Falha de conexão com os servidores da Anthropic: {exc}") from exc
        except anthropic.APIError as exc:
            raise LLMError(self.provider_name, f"Erro na API da Anthropic: {exc}", getattr(exc, "status_code", None)) from exc
        except Exception as exc:
            raise LLMError(self.provider_name, f"Erro inesperado: {exc}") from exc
