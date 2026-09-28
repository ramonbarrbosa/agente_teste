"""Testes para o módulo de configuração e validação do config.yaml."""

import pytest
from pydantic import ValidationError

from src.config import AppConfig, load_config


def test_load_default_config():
    """Garante que o config.yaml da raiz é válido e carrega com sucesso."""
    config = load_config("config.yaml")
    assert isinstance(config, AppConfig)
    assert config.assistant.name == "Prof. Ada - Engenharia de Dados & IA"
    assert config.ui.primary_color == "#2563EB"
    assert config.ui.logo_path == "assets/logo.png"
    assert "openrouter" in config.llm.provider_priority
    assert len(config.ui.examples) >= 1


def test_invalid_hex_color(tmp_path):
    """Garante que cores fora do formato #RRGGBB são rejeitadas."""
    invalid_yaml = tmp_path / "config.yaml"
    invalid_yaml.write_text(
        """
assistant:
  name: "Assistente Teste"
  description: "Descrição válida para teste do validador"
  system_prompt: "Prompt pedagógico de teste com mais de dez caracteres"
ui:
  primary_color: "azul-invalido"
  secondary_color: "#1E293B"
  logo_path: "assets/logo.png"
  examples: ["Pergunta 1"]
llm:
  provider_priority: ["openrouter"]
  providers:
    openrouter:
      model: "google/gemma-4-31b-it:free"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError) as excinfo:
        load_config(str(invalid_yaml))
    assert "hexadecimal de 6 dígitos" in str(excinfo.value)


def test_missing_logo_file(tmp_path):
    """Garante que apontar para um arquivo de logo inexistente falha a validação."""
    invalid_yaml = tmp_path / "config.yaml"
    invalid_yaml.write_text(
        """
assistant:
  name: "Assistente Teste"
  description: "Descrição válida para teste do validador"
  system_prompt: "Prompt pedagógico de teste com mais de dez caracteres"
ui:
  primary_color: "#2563EB"
  secondary_color: "#1E293B"
  logo_path: "assets/logo_inexistente.png"
  examples: ["Pergunta 1"]
llm:
  provider_priority: ["openrouter"]
  providers:
    openrouter:
      model: "google/gemma-4-31b-it:free"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError) as excinfo:
        load_config(str(invalid_yaml))
    assert "não foi encontrado no repositório" in str(excinfo.value)


def test_duplicate_provider_priority(tmp_path):
    """Garante que provedores duplicados na prioridade são rejeitados."""
    invalid_yaml = tmp_path / "config.yaml"
    invalid_yaml.write_text(
        """
assistant:
  name: "Assistente Teste"
  description: "Descrição válida para teste do validador"
  system_prompt: "Prompt pedagógico de teste com mais de dez caracteres"
ui:
  primary_color: "#2563EB"
  secondary_color: "#1E293B"
  logo_path: "assets/logo.png"
  examples: ["Pergunta 1"]
llm:
  provider_priority: ["openrouter", "openrouter"]
  providers:
    openrouter:
      model: "google/gemma-4-31b-it:free"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError) as excinfo:
        load_config(str(invalid_yaml))
    assert "duplicados" in str(excinfo.value)


def test_priority_provider_missing_in_providers(tmp_path):
    """Garante que provedor na lista de prioridade sem bloco 'providers' é rejeitado."""
    invalid_yaml = tmp_path / "config.yaml"
    invalid_yaml.write_text(
        """
assistant:
  name: "Assistente Teste"
  description: "Descrição válida para teste do validador"
  system_prompt: "Prompt pedagógico de teste com mais de dez caracteres"
ui:
  primary_color: "#2563EB"
  secondary_color: "#1E293B"
  logo_path: "assets/logo.png"
  examples: ["Pergunta 1"]
llm:
  provider_priority: ["openrouter", "openai"]
  providers:
    openrouter:
      model: "google/gemma-4-31b-it:free"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError) as excinfo:
        load_config(str(invalid_yaml))
    assert "não foi configurado em 'providers'" in str(excinfo.value)
