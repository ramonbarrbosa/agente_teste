"""Roteador de modelos com failover inteligente em cascata."""

import logging
from typing import Dict, List

from src.config import AppConfig
from src.providers.anthropic_client import AnthropicProvider
from src.providers.base import BaseLLMProvider, LLMError
from src.providers.openai_client import OpenAIProvider
from src.providers.openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)


class LLMRouter:
    def __init__(self, config: AppConfig):
        self.config = config
        self.system_prompt = config.assistant.system_prompt
        self.max_tokens = config.llm.max_tokens
        self.temperature = config.llm.temperature

        # Inicializa adaptadores de acordo com a configuração
        self._all_providers: Dict[str, BaseLLMProvider] = {
            "openrouter": OpenRouterProvider(model=config.llm.providers["openrouter"].model),
            "openai": OpenAIProvider(model=config.llm.providers["openai"].model),
            "anthropic": AnthropicProvider(model=config.llm.providers["anthropic"].model),
        }

    def get_configured_providers(self) -> List[BaseLLMProvider]:
        """Retorna lista de provedores ativos com chaves disponíveis na ordem de prioridade."""
        available = []
        for name in self.config.llm.provider_priority:
            provider = self._all_providers.get(name)
            if provider and provider.is_available():
                available.append(provider)
        return available

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Executa a chamada aos provedores com fallback automático em cascata."""
        active_providers = self.get_configured_providers()

        if not active_providers:
            return (
                "⚠️ **Atenção: Nenhuma chave de API de IA está configurada no momento.**\n\n"
                "Para que o assistente funcione, configure pelo menos uma das seguintes variáveis nos "
                "**Secrets** do Hugging Face Spaces:\n"
                "- `OPENROUTER_API_KEY` (Recomendado — suporte a modelos gratuitos)\n"
                "- `OPENAI_API_KEY`\n"
                "- `ANTHROPIC_API_KEY`\n\n"
                "Assim que salvar o secret no Space, o assistente responderá automaticamente."
            )

        failures = []

        for provider in active_providers:
            try:
                logger.info(f"Tentando gerar resposta com o provedor: {provider.provider_name}")
                response = provider.generate(
                    messages=messages,
                    system_prompt=self.system_prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                if response.content:
                    return response.content
                else:
                    failures.append(f"• **{provider.provider_name}**: Retornou resposta vazia.")
            except LLMError as exc:
                logger.warning(f"Falha no provedor {provider.provider_name}: {exc.message}")
                failures.append(f"• **{provider.provider_name}**: {exc.message}")
            except Exception as exc:
                logger.error(f"Erro inesperado no provedor {provider.provider_name}: {exc}")
                failures.append(f"• **{provider.provider_name}**: Erro inesperado ({str(exc)})")

        # Se todos os provedores falharem
        return (
            "⚠️ **Desculpe, não consegui obter resposta no momento.**\n\n"
            "Todos os provedores de inteligência artificial disponíveis apresentaram falha:\n\n"
            + "\n".join(failures)
            + "\n\n*Por favor, tente novamente em alguns instantes ou verifique as cotas e limites das chaves.*"
        )
