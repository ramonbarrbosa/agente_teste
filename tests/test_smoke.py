"""Teste de fumaça (smoke test) para validar a instanciação da interface Gradio."""

import gradio as gr

from src.config import load_config
from src.providers.router import LLMRouter
from src.ui import build_app


def test_gradio_app_smoke():
    """Garante que a interface gráfica é construída e compilada sem exceções."""
    config = load_config("config.yaml")
    router = LLMRouter(config)
    demo = build_app(config, router)

    assert isinstance(demo, gr.Blocks)
    assert demo.title == config.assistant.name
