"""Testes para o LLMRouter cobrindo failover em cascata e mensagens de erro."""

from unittest.mock import MagicMock

from src.config import load_config
from src.providers.base import LLMError, LLMResponse
from src.providers.router import LLMRouter


def test_router_no_keys_configured(monkeypatch):
    """Quando nenhuma chave está configurada, retorna mensagem de aviso amigável."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    config = load_config("config.yaml")
    router = LLMRouter(config)

    response = router.generate_response([{"role": "user", "content": "Olá"}])
    assert "Nenhuma chave de API de IA está configurada" in response
    assert "OPENROUTER_API_KEY" in response


def test_router_failover_first_fails_second_succeeds(monkeypatch):
    """Simula falha no 1º provedor (ex: 429) e sucesso no 2º (failover perfeito)."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-openrouter-key")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    config = load_config("config.yaml")
    router = LLMRouter(config)

    # Mock do OpenRouter para falhar
    mock_openrouter = MagicMock()
    mock_openrouter.provider_name = "OpenRouter"
    mock_openrouter.is_available.return_value = True
    mock_openrouter.generate.side_effect = LLMError("OpenRouter", "Limite de cota excedido (429)", 429)

    # Mock da OpenAI para ter sucesso
    mock_openai = MagicMock()
    mock_openai.provider_name = "OpenAI"
    mock_openai.is_available.return_value = True
    mock_openai.generate.return_value = LLMResponse(
        content="Olá! Sou a Prof. Ada respondendo via OpenAI.",
        provider="OpenAI",
        model="gpt-4o-mini",
    )

    router._all_providers["openrouter"] = mock_openrouter
    router._all_providers["openai"] = mock_openai

    response = router.generate_response([{"role": "user", "content": "Explique SQL"}])

    assert response == "Olá! Sou a Prof. Ada respondendo via OpenAI."
    mock_openrouter.generate.assert_called_once()
    mock_openai.generate.assert_called_once()


def test_router_all_providers_fail(monkeypatch):
    """Quando todos os provedores ativos falham, retorna relatório com a causa de cada um."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-openrouter-key")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    config = load_config("config.yaml")
    router = LLMRouter(config)

    mock_openrouter = MagicMock()
    mock_openrouter.provider_name = "OpenRouter"
    mock_openrouter.is_available.return_value = True
    mock_openrouter.generate.side_effect = LLMError("OpenRouter", "Serviço indisponível (503)", 503)

    mock_openai = MagicMock()
    mock_openai.provider_name = "OpenAI"
    mock_openai.is_available.return_value = True
    mock_openai.generate.side_effect = LLMError("OpenAI", "Saldo insuficiente (402)", 402)

    router._all_providers["openrouter"] = mock_openrouter
    router._all_providers["openai"] = mock_openai

    response = router.generate_response([{"role": "user", "content": "Explique SQL"}])

    assert "Todos os provedores de inteligência artificial disponíveis apresentaram falha" in response
    assert "OpenRouter" in response
    assert "Serviço indisponível (503)" in response
    assert "OpenAI" in response
    assert "Saldo insuficiente (402)" in response
