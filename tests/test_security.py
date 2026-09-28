"""Teste de segurança automatizado para prevenir vazamento acidental de chaves de API."""

import os
import re

# Padrões conhecidos de chaves de API reais
SUSPICIOUS_KEY_PATTERNS = [
    (re.compile(r"sk-ant-[a-zA-Z0-9_\-]{20,}"), "Chave de API da Anthropic detectada!"),
    (re.compile(r"sk-(?!test|fake|placeholder|none)[a-zA-Z0-9_\-]{30,}"), "Chave de API OpenAI/OpenRouter detectada!"),
    (re.compile(r"hf_[a-zA-Z0-9]{30,}"), "Token de acesso do Hugging Face detectado!"),
]

# Pastas e arquivos ignorados na varredura
IGNORED_DIRS = {".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache", ".ruff_cache"}
IGNORED_FILES = {".gitignore"}
BINARY_EXTENSIONS = {".png", ".jpg", ".jpeg", ".ico", ".svg", ".pyc", ".lock"}


def test_no_api_keys_leaked_in_repository():
    """Varre todo o repositório para garantir que nenhuma chave real de API foi commitada."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    leaks = []

    for root, dirs, files in os.walk(repo_root):
        # Filtra diretórios ignorados
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            if file in IGNORED_FILES:
                continue

            _, ext = os.path.splitext(file)
            if ext.lower() in BINARY_EXTENSIONS:
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_root)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            for pattern, message in SUSPICIOUS_KEY_PATTERNS:
                matches = pattern.findall(content)
                if matches:
                    leaks.append(f"{rel_path}: {message} (Tamanho: {len(matches[0])} caracteres)")

    assert not leaks, (
        "ALERTA CRÍTICO DE SEGURANÇA: Chaves de API detectadas em arquivos do repositório!\n"
        + "\n".join(leaks)
        + "\nRemova as chaves e configure-as apenas nos Secrets do Hugging Face."
    )
