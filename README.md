---
title: Prof. Ada - Engenharia de Dados & IA
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.20.0
app_file: app.py
pinned: false
license: mit
---

# 🎓 Prof. Ada — Assistente de Engenharia de Dados & IA

Este assistente foi desenvolvido para responder dúvidas pedagógicas sobre Engenharia de Dados e Inteligência Artificial, funcionando com alta disponibilidade por meio de um sistema de fallback inteligente entre provedores de IA (**OpenRouter**, **OpenAI** e **Anthropic**).

## 🚀 Como Funciona

- **Interface**: Construída em [Gradio](https://www.gradio.app/) e hospedada gratuitamente no Hugging Face Spaces.
- **Failover em Cascata**: Tenta o provedor prioritário (ex: modelos gratuitos no OpenRouter). Se falhar (cota atingida ou indisponibilidade), tenta os próximos provedores cadastrados automaticamente.
- **Configuração Sem Código**: Todo o comportamento, visual, cores e exemplos são configurados pelo arquivo `config.yaml`.
- **CI/CD Automatizado**: Validações automáticas de schema, testes e prevenção de vazamento de credenciais antes do deploy via GitHub Actions.

## 🛠️ Personalização

Para alterar o nome, instruções ou modelos, edite o arquivo [`config.yaml`](config.yaml) diretamente no GitHub.

## 🔒 Segurança

Nenhuma chave de API fica armazenada neste repositório. As chaves devem ser cadastradas nos **Secrets** do Space no Hugging Face:
- `OPENROUTER_API_KEY`
- `OPENAI_API_KEY` (opcional)
- `ANTHROPIC_API_KEY` (opcional)
