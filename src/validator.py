"""Script CLI para validação autônoma do arquivo de configuração no CI/CD."""

import os
import sys

# Garante que a raiz do projeto esteja no sys.path mesmo se chamado diretamente
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from pydantic import ValidationError  # noqa: E402

from src.config import load_config  # noqa: E402


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    print(f"🔍 Validando arquivo de configuração: {config_path}")

    try:
        config = load_config(config_path)
        print("✅ Configuração validada com sucesso!")
        print(f"   • Assistente: {config.assistant.name}")
        print(f"   • Provedores ativos: {', '.join(config.llm.provider_priority)}")
        print(f"   • Perguntas de exemplo: {len(config.ui.examples)}")
        print(f"   • Logotipo: {config.ui.logo_path} (Largura: {config.ui.logo_width}px)")
        return 0
    except (FileNotFoundError, ValueError, ValidationError) as exc:
        print("\n❌ ERRO NA CONFIGURAÇÃO DETECTADO:")
        print(f"   {exc}")
        print("\nPor favor, corrija o arquivo de configuração antes de publicar.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
