#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSPETOR DE QUALIDADE & AUDITORIA - PORTAL ÍMPROBO
Responsável pelo 'Portão de Segurança' obrigatório:
- Validação estrita de texto, áudio e caricatura
- Registro de histórico de execuções
- Radar de pautas quentes para o painel de controle
"""

import os
import json
import time
from datetime import datetime, timezone
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_DB_PATH = os.path.join(BASE_DIR, "status_db.json")
IMAGENS_DIR = os.path.join(BASE_DIR, "imagens")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
CONTENT_DIR = os.path.join(BASE_DIR, "content")

def carregar_status_db():
    """Carrega o histórico e telemetria do sistema"""
    if os.path.exists(STATUS_DB_PATH):
        try:
            with open(STATUS_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "ultima_atualizacao": datetime.now(timezone.utc).isoformat(),
        "status_apis": {
            "gemini": "online",
            "feeds": "online",
            "audio": "online",
            "vercel": "online"
        },
        "historico_execucoes": [],
        "radar_pautas": []
    }

def salvar_status_db(dados):
    """Persiste dados de telemetria em status_db.json"""
    dados["ultima_atualizacao"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(STATUS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Erro ao salvar status_db.json: {e}")

def validar_artigo_completo(dados_artigo):
    """
    PORTÃO DE SEGURANÇA MANDATÓRIO (Checklist 5 Pontos):
    1. Estrutura Textual Satírica
    2. Imagem Caricatura Real (> 50KB e dimensões válidas)
    3. Narração Neural em Áudio
    Retorna: (sucesso: bool, mensagem_diagnostico: str)
    """
    if not isinstance(dados_artigo, dict):
        return False, "Estrutura do artigo inválida (não é um dicionário JSON)."

    slug = dados_artigo.get("slug")
    if not slug:
        return False, "Slug do artigo ausente ou vazio."

    # 1. Validação de Título e Subtítulo
    titulo = dados_artigo.get("titulo", "").strip()
    if not titulo or len(titulo) < 10:
        return False, f"Título inválido ou muito curto: '{titulo}'."

    subtitulo = dados_artigo.get("subtitulo", "").strip()
    if not subtitulo or len(subtitulo) < 20:
        return False, "Subtítulo explicativo ausente ou curto demais."

    # 2. Validação do Corpo da Crônica
    corpo = dados_artigo.get("corpo", [])
    if not isinstance(corpo, list) or len(corpo) < 3:
        return False, f"Corpo do texto incompleto (esperado no mínimo 3 parágrafos, encontrados {len(corpo)})."

    for idx, p in enumerate(corpo, start=1):
        if len(p.strip()) < 80:
            return False, f"Parágrafo {idx} muito curto para o padrão editorial ÍMPROBO."

    # 3. REGRA DE OURO SAGRADA: Validação Estrita de Caricatura
    caminho_img = os.path.join(IMAGENS_DIR, f"{slug}.jpg")
    if not os.path.exists(caminho_img):
        return False, f"Arquivo de caricatura não encontrado em disco: imagens/{slug}.jpg"

    tamanho_bytes = os.path.getsize(caminho_img)
    if tamanho_bytes < 50000:
        return False, f"Caricatura rejeitada por tamanho insuficiente ({tamanho_bytes} bytes). Esperado >= 50KB."

    try:
        with Image.open(caminho_img) as im:
            largura, altura = im.size
            if largura < 800 or altura < 450:
                return False, f"Resolução da imagem abaixo do padrão widescreen ({largura}x{altura})."
            if im.format not in ("JPEG", "PNG", "WEBP"):
                return False, f"Formato de imagem inválido ({im.format})."
    except Exception as e:
        return False, f"Arquivo de imagem corrompido ou ilegível: {e}"

    # 4. Validação Mandatória de Narração Neural em Áudio
    caminho_audio = os.path.join(AUDIO_DIR, f"{slug}.mp3")
    if not os.path.exists(caminho_audio):
        return False, f"Arquivo de áudio neural não encontrado em disco: audio/{slug}.mp3"

    tamanho_audio = os.path.getsize(caminho_audio)
    if tamanho_audio < 50000:
        return False, f"Áudio neural incompleto ou corrompido ({tamanho_audio} bytes). Esperado >= 50KB."

    return True, "Artigo 100% aprovado em todos os critérios de qualidade e padrões visuais."

def registrar_execucao(status, motivo, dados_artigo=None, duracao_seg=0):
    """Registra o histórico da rodada no banco de telemetria"""
    db = carregar_status_db()
    agora_brt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "horario_brt": agora_brt,
        "status": status, # "SUCESSO", "RETIDO", "ERRO"
        "motivo": motivo,
        "duracao_segundos": round(duracao_seg, 1),
        "slug": dados_artigo.get("slug") if dados_artigo else None,
        "titulo": dados_artigo.get("titulo") if dados_artigo else None,
        "imagem_tamanho_kb": round(os.path.getsize(os.path.join(IMAGENS_DIR, f"{dados_artigo['slug']}.jpg")) / 1024, 1) if (dados_artigo and os.path.exists(os.path.join(IMAGENS_DIR, f"{dados_artigo['slug']}.jpg"))) else 0,
        "audio_tamanho_kb": round(os.path.getsize(os.path.join(AUDIO_DIR, f"{dados_artigo['slug']}.mp3")) / 1024, 1) if (dados_artigo and os.path.exists(os.path.join(AUDIO_DIR, f"{dados_artigo['slug']}.mp3"))) else 0
    }

    # Mantém os últimos 20 registros
    db["historico_execucoes"].insert(0, registro)
    db["historico_execucoes"] = db["historico_execucoes"][:20]
    salvar_status_db(db)
    print(f"[✓] Execução registrada no histórico com status: {status}")

def atualizar_radar_pautas(noticias_ranqueadas):
    """Atualiza o Top 5 de pautas quentes vigiadas pelo robô"""
    db = carregar_status_db()
    radar = []
    for score, n in noticias_ranqueadas[:5]:
        radar.append({
            "titulo": n.get("titulo"),
            "fonte": n.get("fonte"),
            "link": n.get("link"),
            "score": score,
            "data_pub": n.get("data_pub")
        })
    db["radar_pautas"] = radar
    salvar_status_db(db)
    print(f"[✓] Radar de pautas atualizado no painel: {len(radar)} notícias em monitoramento.")

if __name__ == "__main__":
    print("[*] Testando Inspetor de Qualidade...")
    db = carregar_status_db()
    print(f"[✓] Status DB carregado com {len(db.get('historico_execucoes', []))} execuções.")
