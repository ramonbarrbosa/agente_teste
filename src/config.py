"""Módulo de carregamento e validação estrita da configuração do assistente."""

import os
import re
from typing import Dict, List, Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
VALID_PROVIDERS = {"openrouter", "openai", "anthropic"}


class AssistantConfig(BaseModel):
    name: str = Field(..., min_length=3, max_length=60, description="Nome do assistente")
    description: str = Field(..., min_length=10, max_length=300, description="Frase de descrição")
    system_prompt: str = Field(..., min_length=10, description="Instruções pedagógicas e de persona")


class UIConfig(BaseModel):
    primary_color: str = Field("#2563EB", description="Cor primária da interface em hexadecimal")
    secondary_color: str = Field("#1E293B", description="Cor secundária da interface em hexadecimal")
    logo_path: str = Field("assets/logo.png", description="Caminho relativo para imagem da logo")
    logo_width: int = Field(80, ge=32, le=300, description="Largura da logo em pixels")
    examples: List[str] = Field(..., min_length=1, max_length=6, description="Perguntas de exemplo para o chat")

    @field_validator("primary_color", "secondary_color")
    @classmethod
    def validate_hex_color(cls, value: str) -> str:
        if not HEX_COLOR_PATTERN.match(value.strip()):
            raise ValueError(
                f"Cor '{value}' inválida. Deve ser um código hexadecimal de 6 dígitos (exemplo: #2563EB)."
            )
        return value.strip().upper()

    @field_validator("logo_path")
    @classmethod
    def validate_logo_file(cls, value: str) -> str:
        clean_path = value.strip()
        if not os.path.isfile(clean_path):
            raise ValueError(
                f"O arquivo de logotipo '{clean_path}' não foi encontrado no repositório. "
                f"Verifique se o caminho está correto e o arquivo foi commitado."
            )
        return clean_path


class ProviderModelConfig(BaseModel):
    model: str = Field(..., min_length=1, description="Identificador do modelo do provedor")


class LLMConfig(BaseModel):
    max_tokens: int = Field(1024, ge=128, le=4096, description="Limite máximo de tokens gerados")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Criatividade da resposta")
    provider_priority: List[Literal["openrouter", "openai", "anthropic"]] = Field(
        ..., min_length=1, description="Ordem de preferência dos provedores"
    )
    providers: Dict[str, ProviderModelConfig] = Field(
        ..., description="Configuração específica de modelo para cada provedor"
    )

    @field_validator("provider_priority")
    @classmethod
    def validate_unique_priority(cls, value: List[str]) -> List[str]:
        if len(value) != len(set(value)):
            raise ValueError("A lista 'provider_priority' não pode conter provedores duplicados.")
        return value

    @model_validator(mode="after")
    def validate_providers_declared(self) -> "LLMConfig":
        for provider_name in self.provider_priority:
            if provider_name not in self.providers:
                raise ValueError(
                    f"O provedor '{provider_name}' está em 'provider_priority', mas não foi configurado em 'providers'."
                )
        return self


class AppConfig(BaseModel):
    assistant: AssistantConfig
    ui: UIConfig
    llm: LLMConfig


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """Lê, analisa e valida o arquivo de configuração YAML."""
    if not os.path.isfile(config_path):
        raise FileNotFoundError(
            f"Arquivo de configuração '{config_path}' não encontrado. "
            f"Certifique-se de que ele existe na raiz do projeto."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"Erro de sintaxe no arquivo YAML '{config_path}': {exc}") from exc

    if not isinstance(raw_data, dict):
        raise ValueError(f"O conteúdo de '{config_path}' deve ser um mapeamento YAML (dicionário).")

    return AppConfig.model_validate(raw_data)
