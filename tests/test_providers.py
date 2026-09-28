"""Testes unitários dos clientes de provedores com simulações (mocks)."""

from unittest.mock import MagicMock, patch

from src.providers.anthropic_client import AnthropicProvider
from src.providers.base import LLMResponse
from src.providers.openai_client import OpenAIProvider
from src.providers.openrouter import OpenRouterProvider


def test_openrouter_availability(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    provider = OpenRouterProvider()
    assert not provider.is_available()

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-123")
    provider = OpenRouterProvider()
    assert provider.is_available()


def test_openrouter_generation_success(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-test-key")
    provider = OpenRouterProvider(model="google/gemma-4-31b-it:free")

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Resposta simulada OpenRouter"
    mock_response = MagicMock(choices=[mock_choice])
    mock_client.chat.completions.create.return_value = mock_response

    with patch("openai.OpenAI", return_value=mock_client):
        result = provider.generate([{"role": "user", "content": "Olá"}], "Prompt de sistema")

    assert isinstance(result, LLMResponse)
    assert result.content == "Resposta simulada OpenRouter"
    assert result.provider == "OpenRouter"


def test_openai_generation_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-test-key")
    provider = OpenAIProvider(model="gpt-4o-mini")

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Resposta simulada OpenAI"
    mock_response = MagicMock(choices=[mock_choice])
    mock_client.chat.completions.create.return_value = mock_response

    with patch("openai.OpenAI", return_value=mock_client):
        result = provider.generate([{"role": "user", "content": "Olá"}], "Prompt de sistema")

    assert isinstance(result, LLMResponse)
    assert result.content == "Resposta simulada OpenAI"
    assert result.provider == "OpenAI"


def test_anthropic_generation_success(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-test-key")
    provider = AnthropicProvider(model="claude-3-5-haiku-latest")

    mock_client = MagicMock()
    mock_block = MagicMock()
    mock_block.text = "Resposta simulada Anthropic"
    mock_response = MagicMock(content=[mock_block])
    mock_client.messages.create.return_value = mock_response

    with patch("anthropic.Anthropic", return_value=mock_client):
        result = provider.generate([{"role": "user", "content": "Olá"}], "Prompt de sistema")

    assert isinstance(result, LLMResponse)
    assert result.content == "Resposta simulada Anthropic"
    assert result.provider == "Anthropic"
