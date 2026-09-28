"""Ponto de entrada do aplicativo Gradio para o Hugging Face Spaces."""

import logging
import os

from src.config import load_config
from src.providers.router import LLMRouter
from src.ui import build_app

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agente_teste")

# Carrega a configuração validada
logger.info("Carregando configuração a partir de config.yaml...")
config = load_config("config.yaml")

# Inicializa roteador de inteligência artificial
logger.info("Inicializando roteador de LLMs...")
router = LLMRouter(config)

# Constrói a interface Gradio
logger.info(f"Construindo interface para '{config.assistant.name}'...")
app = build_app(config, router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    logger.info(f"Iniciando servidor Gradio na porta {port}...")
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        show_error=True,
    )
