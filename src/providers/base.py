"""Interface base e estruturas de dados comuns para provedores de IA."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str


class LLMError(Exception):
    def __init__(self, provider: str, message: str, status_code: Optional[int] = None):
        self.provider = provider
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")


class BaseLLMProvider(ABC):
    """Interface abstrata para clientes de LLM."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nome legível do provedor."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Indica se o provedor possui credenciais válidas configuradas no ambiente."""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Gera resposta para a lista de mensagens."""
        pass
