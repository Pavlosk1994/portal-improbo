#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTIFICADOR TELEGRAM - PORTAL ÍMPROBO
Envia relatórios automáticos e alertas em tempo real direto para o celular do editor.
100% gratuito e seguro.
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

def obter_config_telegram():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    return token, chat_id

def enviar_mensagem_telegram(texto_markdown):
    token, chat_id = obter_config_telegram()
    if not token or not chat_id:
        # Se as credenciais ainda não foram cadastradas, registra aviso silencioso
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto_markdown,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[!] Erro ao enviar notificação Telegram: {e}")
        return False

def notificar_sucesso(dados_artigo, portal_url="https://portal-improbo.vercel.app"):
    """Dispara notificação verde de sucesso com resumo da edição"""
    titulo = dados_artigo.get("titulo", "NOVA CRÔNICA")
    subtitulo = dados_artigo.get("subtitulo", "")
    slug = dados_artigo.get("slug", "")
    link = f"{portal_url.rstrip('/')}/artigos/{slug}.html"
    hora = datetime.now().strftime("%H:%M BRT")

    msg = (
        f"🟢 *ÍMPROBO • EDIÇÃO PUBLICADA COM SUCESSO*\n"
        f"⏰ *Horário:* {hora}\n\n"
        f"📰 *{titulo}*\n"
        f"_{subtitulo}_\n\n"
        f"🖼️ *Caricatura Editorial:* Validada ✓ (Estilo Pasquim/MAD)\n"
        f"🎙️ *Narração Neural:* Validada ✓\n\n"
        f"🔗 [Clique aqui para ler no ar]({link})"
    )
    return enviar_mensagem_telegram(msg)

def notificar_alerta(motivo, detalhe=""):
    """Dispara alerta vermelho quando uma publicação é retida com segurança"""
    hora = datetime.now().strftime("%H:%M BRT")
    msg = (
        f"🔴 *ALERTA ÍMPROBO • PUBLICAÇÃO RETIDA*\n"
        f"⏰ *Horário:* {hora}\n\n"
        f"⚠️ *Motivo:* {motivo}\n"
    )
    if detalhe:
        msg += f"ℹ️ *Detalhes:* `{detalhe}`\n\n"
    msg += (
        f"🛡️ *Ação de Segurança:* O robô cancelou o deploy. Nenhuma matéria sem imagem ou fora do padrão foi publicada."
    )
    return enviar_mensagem_telegram(msg)

if __name__ == "__main__":
    t, c = obter_config_telegram()
    if t and c:
        print("[*] Testando envio de mensagem...")
        enviar_mensagem_telegram("🚀 *Ímprobo:* Teste de conexão do Notificador Telegram!")
    else:
        print("[i] Credenciais do Telegram não configuradas no momento (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID).")

