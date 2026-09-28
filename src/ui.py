"""Interface visual do assistente construída com Gradio."""

import base64
import os
from typing import List, Tuple

import gradio as gr

from src.config import AppConfig
from src.providers.router import LLMRouter


def get_image_base64(image_path: str) -> str:
    """Converte imagem local para data URI base64 seguro para renderização HTML."""
    if not os.path.isfile(image_path):
        return ""
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext == "svg":
        mime = "image/svg+xml"
    elif ext in ("jpg", "jpeg"):
        mime = "image/jpeg"
    else:
        mime = "image/png"

    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def build_app(config: AppConfig, router: LLMRouter) -> gr.Blocks:
    """Constrói a interface Gradio Blocks completa com base na configuração."""
    logo_base64 = get_image_base64(config.ui.logo_path)
    primary_color = config.ui.primary_color
    secondary_color = config.ui.secondary_color

    custom_css = f"""
    .header-container {{
        display: flex;
        align-items: center;
        gap: 1.25rem;
        padding: 1.2rem 1.5rem;
        background: linear-gradient(135deg, {secondary_color} 0%, #0F172A 100%);
        border-radius: 12px;
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}
    .header-logo {{
        width: {config.ui.logo_width}px;
        height: auto;
        border-radius: 8px;
        object-fit: contain;
    }}
    .header-title {{
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
    }}
    .header-desc {{
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
        color: #94A3B8;
        line-height: 1.4;
    }}
    .gradio-container {{
        max-width: 960px !important;
        margin: 0 auto !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    .send-btn {{
        background-color: {primary_color} !important;
        color: white !important;
        font-weight: 600 !important;
    }}
    """

    with gr.Blocks(title=config.assistant.name) as demo:
        # Injeção de estilos CSS personalizados e cabeçalho da aplicação
        logo_html = (
            f'<img src="{logo_base64}" class="header-logo" alt="Logo">'
            if logo_base64
            else ""
        )
        gr.HTML(
            f"""
            <style>
            {custom_css}
            </style>
            <div class="header-container">
                {logo_html}
                <div>
                    <h1 class="header-title">{config.assistant.name}</h1>
                    <p class="header-desc">{config.assistant.description}</p>
                </div>
            </div>
            """
        )

        chatbot = gr.Chatbot(
            label="Conversa",
            height=480,
        )

        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Digite sua dúvida sobre Engenharia de Dados ou Inteligência Artificial...",
                label="Sua pergunta",
                scale=8,
                lines=1,
                autofocus=True,
            )
            send_btn = gr.Button("Enviar", variant="primary", scale=2, elem_classes=["send-btn"])

        with gr.Row():
            gr.ClearButton([msg_input, chatbot], value="Limpar Conversa", size="sm")

        # Seção de perguntas de exemplo
        if config.ui.examples:
            gr.Examples(
                examples=config.ui.examples,
                inputs=msg_input,
                label="💡 Perguntas frequentes (clique para preencher)",
            )

        def user_submit(user_msg: str, chat_history: List[Tuple[str, str]]):
            if not user_msg or not user_msg.strip():
                return "", chat_history
            updated_history = chat_history + [(user_msg, "")]
            return "", updated_history

        def bot_respond(chat_history: List[Tuple[str, str]]):
            if not chat_history:
                return chat_history

            user_msg = chat_history[-1][0]

            # Monta histórico de mensagens no formato role/content
            llm_messages = []
            for past_user, past_bot in chat_history[:-1]:
                if past_user:
                    llm_messages.append({"role": "user", "content": past_user})
                if past_bot:
                    llm_messages.append({"role": "assistant", "content": past_bot})

            llm_messages.append({"role": "user", "content": user_msg})

            bot_reply = router.generate_response(llm_messages)
            chat_history[-1] = (user_msg, bot_reply)
            return chat_history

        # Encadeamento de eventos: limpa input -> adiciona ao chat -> gera resposta
        msg_input.submit(
            fn=user_submit,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot],
            queue=False,
        ).then(
            fn=bot_respond,
            inputs=[chatbot],
            outputs=[chatbot],
        )

        send_btn.click(
            fn=user_submit,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot],
            queue=False,
        ).then(
            fn=bot_respond,
            inputs=[chatbot],
            outputs=[chatbot],
        )

    return demo
