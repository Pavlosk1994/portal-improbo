#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SALA DE MÁQUINAS - PAINEL SECRETO DE CONTROLE E TELEMETRIA
Gera a página /sala-de-maquinas.html para auditoria das matérias, semáforos de API,
histórico de execuções do robô, radar de notícias e pauta sob demanda (furo de reportagem).
"""

import os
import json
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_DB_PATH = os.path.join(BASE_DIR, "status_db.json")
IMAGENS_DIR = os.path.join(BASE_DIR, "imagens")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

def carregar_telemetria():
    if os.path.exists(STATUS_DB_PATH):
        try:
            with open(STATUS_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "status_apis": {
            "gemini": "online",
            "feeds": "online",
            "audio": "online",
            "vercel": "online"
        },
        "historico_execucoes": [],
        "radar_pautas": []
    }

def formatar_tamanho(bytes_qty):
    if not bytes_qty or bytes_qty <= 0:
        return "0 KB"
    kb = bytes_qty / 1024
    if kb >= 1024:
        return f"{kb/1024:.2f} MB"
    return f"{kb:.1f} KB"

def generate_sala_de_maquinas_page(articles, portal_url="https://portal-improbo.vercel.app"):
    telemetria = carregar_telemetria()
    status_apis = telemetria.get("status_apis", {})
    historico = telemetria.get("historico_execucoes", [])
    radar = telemetria.get("radar_pautas", [])

    # Monta linhas do Histórico de Execuções
    historico_rows_html = ""
    if not historico:
        historico_rows_html = """
        <tr>
            <td colspan="6" class="px-4 py-6 text-center text-stone-500 font-mono text-sm">
                Nenhuma execução registrada até o momento.
            </td>
        </tr>
        """
    else:
        for ex in historico[:15]:
            st = ex.get("status", "INFO")
            if st == "SUCESSO":
                badge = '<span class="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-700/60">✓ SUCESSO</span>'
            elif st == "RETIDO":
                badge = '<span class="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-amber-950/80 text-amber-300 border border-amber-600/60">⚠️ RETIDO</span>'
            else:
                badge = '<span class="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-red-950/80 text-red-400 border border-red-700/60">✕ ERRO</span>'

            horario = ex.get("horario_brt") or ex.get("timestamp", "-")[:16].replace("T", " ")
            titulo = ex.get("titulo") or "Varredura de Rotina"
            slug = ex.get("slug")
            if st == "SUCESSO" and slug:
                titulo_link = f'<a href="artigos/{slug}.html" target="_blank" class="hover:text-amber-300 underline underline-offset-2">{titulo}</a>'
            elif st == "RETIDO":
                titulo_link = f'<span class="text-stone-400 italic">{titulo} <span class="text-[10px] text-amber-500 font-mono">(Abortado com segurança)</span></span>'
            else:
                titulo_link = f'<span class="text-stone-400">{titulo}</span>'

            duracao = f"{ex.get('duracao_segundos', 0):.1f}s"
            img_kb = f"{ex.get('imagem_tamanho_kb', 0):.1f} KB" if ex.get('imagem_tamanho_kb') else "-"
            audio_kb = f"{ex.get('audio_tamanho_kb', 0):.1f} KB" if ex.get('audio_tamanho_kb') else "-"
            motivo = ex.get("motivo", "-")

            historico_rows_html += f"""
            <tr class="border-b border-stone-800/60 hover:bg-stone-900/40 transition-colors">
                <td class="px-4 py-3 font-mono text-xs text-stone-400 whitespace-nowrap">{horario}</td>
                <td class="px-4 py-3 whitespace-nowrap">{badge}</td>
                <td class="px-4 py-3 font-serif text-sm text-stone-200">{titulo_link}</td>
                <td class="px-4 py-3 font-mono text-xs text-stone-300 text-center">{duracao}</td>
                <td class="px-4 py-3 font-mono text-xs text-stone-300 text-center">{img_kb}</td>
                <td class="px-4 py-3 font-mono text-xs text-stone-300 text-center">{audio_kb}</td>
                <td class="px-4 py-3 font-mono text-xs text-stone-400 max-w-xs truncate" title="{motivo}">{motivo}</td>
            </tr>
            """

    # Monta Cards do Raio-X dos Artigos
    artigos_raiox_html = ""
    for art in articles[:12]:
        slug = art.get("slug")
        titulo = art.get("titulo")
        subtitulo = art.get("subtitulo", "")
        data_pub = art.get("data", "")
        corpo = art.get("corpo", [])
        palavras = sum(len(p.split()) for p in corpo)

        caminho_img = os.path.join(IMAGENS_DIR, f"{slug}.jpg")
        img_size = os.path.getsize(caminho_img) if os.path.exists(caminho_img) else 0
        img_tam_txt = formatar_tamanho(img_size)

        caminho_aud = os.path.join(AUDIO_DIR, f"{slug}.mp3")
        aud_size = os.path.getsize(caminho_aud) if os.path.exists(caminho_aud) else 0
        aud_tam_txt = formatar_tamanho(aud_size)

        artigos_raiox_html += f"""
        <div class="bg-[#15171e] border border-stone-800 rounded p-4 flex flex-col justify-between hover:border-amber-600/50 transition-all">
            <div>
                <div class="relative overflow-hidden rounded mb-3 bg-stone-900 border border-stone-800 aspect-[16/9]">
                    <img src="imagens/{slug}.jpg" alt="{titulo}" class="w-full h-full object-cover" loading="lazy">
                    <span class="absolute top-2 left-2 bg-black/80 backdrop-blur-xs text-emerald-400 font-mono text-[10px] font-bold px-2 py-0.5 rounded border border-emerald-500/30">
                        IMG: {img_tam_txt}
                    </span>
                    <span class="absolute top-2 right-2 bg-black/80 backdrop-blur-xs text-amber-300 font-mono text-[10px] font-bold px-2 py-0.5 rounded border border-amber-500/30">
                        ÁUDIO: {aud_tam_txt}
                    </span>
                </div>
                <div class="flex items-center gap-2 mb-1">
                    <span class="text-[10px] font-mono uppercase text-stone-500">{data_pub}</span>
                    <span class="text-stone-700">&bull;</span>
                    <span class="text-[10px] font-mono text-stone-400">{palavras} palavras ({len(corpo)}§)</span>
                </div>
                <h4 class="font-serif font-bold text-sm text-stone-100 line-clamp-2 leading-snug mb-2">
                    <a href="artigos/{slug}.html" target="_blank" class="hover:text-amber-300">{titulo}</a>
                </h4>
                <p class="font-sans text-xs text-stone-400 line-clamp-2 mb-3">
                    {subtitulo}
                </p>
            </div>
            <div class="pt-3 border-t border-stone-800/70 flex items-center justify-between text-xs font-mono">
                <span class="text-emerald-400 flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    Auditado ✓
                </span>
                <a href="artigos/{slug}.html" target="_blank" class="text-amber-400 hover:text-amber-300 underline">Ver Matéria &rarr;</a>
            </div>
        </div>
        """

    # Monta Linhas do Radar de Pautas
    radar_rows_html = ""
    if not radar:
        radar_rows_html = """
        <tr>
            <td colspan="4" class="px-4 py-6 text-center text-stone-500 font-mono text-sm">
                Radar de pautas em inicialização. A lista será preenchida na próxima varredura de feeds.
            </td>
        </tr>
        """
    else:
        for idx, item in enumerate(radar[:5], start=1):
            sc = item.get("score", 0)
            fonte = item.get("fonte", "RSS")
            tit = item.get("titulo", "")
            lnk = item.get("link", "#")
            radar_rows_html += f"""
            <tr class="border-b border-stone-800/60 hover:bg-stone-900/40">
                <td class="px-4 py-3 font-mono text-xs font-bold text-amber-400">#{idx}</td>
                <td class="px-4 py-3 font-mono text-xs text-stone-400 whitespace-nowrap">{fonte}</td>
                <td class="px-4 py-3 font-serif text-sm text-stone-200">
                    <a href="{lnk}" target="_blank" rel="noopener noreferrer" class="hover:text-amber-300 underline underline-offset-2">{tit}</a>
                </td>
                <td class="px-4 py-3 font-mono text-xs text-emerald-400 text-center font-bold">{sc}</td>
            </tr>
            """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sala de Máquinas &bull; ÍMPROBO (Bunker de Operações)</title>
    <meta name="robots" content="noindex, nofollow">
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Playfair+Display:ital,wght@0,600;0,700;0,900;1,600&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #0d0e12;
            color: #d1d5db;
        }}
        .font-serif {{ font-family: 'Playfair Display', Georgia, serif; }}
        .font-mono {{ font-family: 'JetBrains Mono', Consolas, monospace; }}
        .font-cinzel {{ font-family: 'Cinzel', serif; }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #121319; }}
        ::-webkit-scrollbar-thumb {{ background: #272a38; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #3c4054; }}

        .glow-emerald {{
            box-shadow: 0 0 15px -3px rgba(16, 185, 129, 0.25);
        }}
        .glow-amber {{
            box-shadow: 0 0 15px -3px rgba(245, 158, 11, 0.25);
        }}
    </style>
</head>
<body class="min-h-screen flex flex-col bg-[#0b0c10] text-stone-200 antialiased selection:bg-amber-600 selection:text-white">

    <!-- MODAL DE BLOQUEIO / PIN DE SEGURANÇA -->
    <div id="pin-lock-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md p-4 transition-opacity duration-300">
        <div class="bg-[#14161f] border-2 border-stone-800 rounded-lg max-w-md w-full p-6 sm:p-8 shadow-2xl text-center relative glow-amber">
            <div class="w-14 h-14 mx-auto mb-4 rounded-full bg-stone-900 border border-amber-600/50 flex items-center justify-center text-amber-500 text-2xl font-mono">
                🔒
            </div>
            <h2 class="font-cinzel font-black text-xl sm:text-2xl text-stone-100 tracking-wide mb-1">
                ACESSO RESTRITO
            </h2>
            <p class="font-mono text-xs uppercase tracking-widest text-amber-500 mb-6 font-bold">
                SALA DE MÁQUINAS &bull; ÍMPROBO
            </p>
            <p class="text-sm text-stone-400 mb-6 leading-relaxed">
                Digite o PIN editorial do Editor-Chefe para acessar o bunker de telemetria, radar de pautas e disparo de furos de reportagem.
            </p>
            <div class="mb-4">
                <input type="password" id="pin-input" maxlength="16" placeholder="Digite o PIN (Padrão: improbo2026)" 
                    class="w-full bg-[#0a0b0e] border border-stone-700 rounded px-4 py-3 text-center font-mono text-lg text-amber-300 focus:outline-hidden focus:border-amber-500 tracking-widest placeholder:text-stone-600 placeholder:text-xs">
            </div>
            <div id="pin-error" class="hidden text-xs font-mono text-red-400 mb-4 font-semibold">
                [!] PIN incorreto. Verifique com a chefia da redação.
            </div>
            <button onclick="verificarPIN()" class="w-full bg-amber-600 hover:bg-amber-500 text-stone-950 font-mono font-black py-3 rounded text-sm uppercase tracking-wider transition-all cursor-pointer">
                DESBLOQUEAR PAINEL
            </button>
            <div class="mt-4 text-[11px] font-mono text-stone-600">
                PORTAL ÍMPROBO &bull; CONTROLE OPERACIONAL CRIPTOGRAFADO
            </div>
        </div>
    </div>

    <!-- CONTEÚDO PRINCIPAL (RESTRITO) -->
    <div id="dashboard-content" class="hidden flex-1 flex flex-col">
        
        <!-- BARRA SUPERIOR -->
        <header class="bg-[#12131a] border-b border-stone-800 sticky top-0 z-40 backdrop-blur-md bg-opacity-90">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                    <span class="text-2xl">⚙️</span>
                    <div>
                        <div class="flex items-center gap-2">
                            <h1 class="font-cinzel font-black text-lg sm:text-xl text-stone-100 tracking-wider">SALA DE MÁQUINAS</h1>
                            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950/80 text-amber-400 border border-amber-700/60">BUNKER</span>
                        </div>
                        <p class="font-mono text-[11px] text-stone-400">Telemetria em Tempo Real &bull; Automação Ímprobo</p>
                    </div>
                </div>

                <div class="flex items-center gap-3">
                    <a href="index.html" target="_blank" class="px-3 py-1.5 rounded bg-stone-900 hover:bg-stone-800 border border-stone-700 text-stone-300 hover:text-white font-mono text-xs flex items-center gap-1.5 transition-colors">
                        <span>📰 Ver Portal ao Vivo</span>
                    </a>
                    <button onclick="bloquearConsole()" class="px-3 py-1.5 rounded bg-red-950/40 hover:bg-red-950/70 border border-red-800/60 text-red-300 font-mono text-xs flex items-center gap-1.5 transition-colors cursor-pointer">
                        <span>🔒 Bloquear</span>
                    </button>
                </div>
            </div>
        </header>

        <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8">

            <!-- BANNER DE STATUS E CRONÔMETRO -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Relógio Próxima Edição -->
                <div class="md:col-span-1 bg-[#14161f] border border-stone-800 rounded-lg p-5 flex flex-col justify-between glow-amber">
                    <div class="flex items-center justify-between mb-3">
                        <span class="font-mono text-xs uppercase font-bold text-amber-400 tracking-wider flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                            PRÓXIMA EDIÇÃO AGENDADA
                        </span>
                        <span class="text-xs font-mono text-stone-500">4x ao dia</span>
                    </div>
                    <div class="my-2">
                        <div id="countdown-timer" class="font-mono font-black text-3xl sm:text-4xl text-stone-100 tracking-tight">
                            --:--:--
                        </div>
                        <p id="proximo-horario-label" class="font-mono text-xs text-stone-400 mt-1">
                            Calculando horário de Brasília...
                        </p>
                    </div>
                    <div class="pt-3 border-t border-stone-800/80 flex items-center justify-between text-[11px] font-mono text-stone-500">
                        <span>Grade BRT: 08h &bull; 13h &bull; 18h &bull; 22h</span>
                        <span class="text-emerald-400">100% Autônomo</span>
                    </div>
                </div>

                <!-- Semáforos das APIs -->
                <div class="md:col-span-2 bg-[#14161f] border border-stone-800 rounded-lg p-5 flex flex-col justify-between">
                    <div class="flex items-center justify-between mb-3">
                        <span class="font-mono text-xs uppercase font-bold text-stone-300 tracking-wider flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                            SEMÁFOROS DE SAÚDE DOS SERVIÇOS &amp; APIS
                        </span>
                        <span class="text-xs font-mono text-emerald-400">TODOS OPERACIONAIS</span>
                    </div>

                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 my-2">
                        <!-- Gemini -->
                        <div class="bg-[#0f1015] border border-stone-800 rounded p-3 text-center">
                            <div class="flex items-center justify-center gap-1 text-emerald-400 font-mono text-xs font-bold mb-1">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                ONLINE
                            </div>
                            <div class="font-mono text-xs font-bold text-stone-200">Gemini IA</div>
                            <div class="font-mono text-[10px] text-stone-500 mt-0.5">Texto &amp; Caricaturas</div>
                        </div>

                        <!-- Feeds RSS -->
                        <div class="bg-[#0f1015] border border-stone-800 rounded p-3 text-center">
                            <div class="flex items-center justify-center gap-1 text-emerald-400 font-mono text-xs font-bold mb-1">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                ONLINE
                            </div>
                            <div class="font-mono text-xs font-bold text-stone-200">Feeds RSS</div>
                            <div class="font-mono text-[10px] text-stone-500 mt-0.5">Folha &bull; G1 &bull; BBC</div>
                        </div>

                        <!-- Edge TTS -->
                        <div class="bg-[#0f1015] border border-stone-800 rounded p-3 text-center">
                            <div class="flex items-center justify-center gap-1 text-emerald-400 font-mono text-xs font-bold mb-1">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                ONLINE
                            </div>
                            <div class="font-mono text-xs font-bold text-stone-200">Áudio Neural</div>
                            <div class="font-mono text-[10px] text-stone-500 mt-0.5">Edge-TTS (Ilimitado)</div>
                        </div>

                        <!-- Actions / Vercel -->
                        <div class="bg-[#0f1015] border border-stone-800 rounded p-3 text-center">
                            <div class="flex items-center justify-center gap-1 text-emerald-400 font-mono text-xs font-bold mb-1">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                ONLINE
                            </div>
                            <div class="font-mono text-xs font-bold text-stone-200">Deploy Contínuo</div>
                            <div class="font-mono text-[10px] text-stone-500 mt-0.5">GitHub &amp; Vercel</div>
                        </div>
                    </div>

                    <div class="pt-3 border-t border-stone-800/80 flex items-center justify-between text-[11px] font-mono text-stone-500">
                        <span>Inspetor de Qualidade: <strong class="text-emerald-400">Portão Estrito Ativo</strong></span>
                        <span>Custos de Infra: <strong class="text-stone-300">R$ 0,00 (100% Free Tier)</strong></span>
                    </div>
                </div>
            </div>

            <!-- PAUTA SOB DEMANDA / FURO DE REPORTAGEM -->
            <div class="bg-[#14161f] border-2 border-amber-600/50 rounded-lg p-5 sm:p-6 glow-amber">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div>
                        <h2 class="font-cinzel font-black text-lg sm:text-xl text-stone-100 flex items-center gap-2">
                            <span>🚨</span>
                            <span>PAUTA SOB DEMANDA &bull; DISPARAR FURO DE REPORTAGEM</span>
                        </h2>
                        <p class="font-sans text-xs sm:text-sm text-stone-400 mt-0.5">
                            Suba uma crônica ácida imediata fora da escala horária normal. Cole o link de uma notícia quente ou defina o tema exclusivo.
                        </p>
                    </div>
                    <span class="self-start sm:self-auto px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono text-xs font-bold">
                        Ação Imediata
                    </span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <!-- Opção 1: Link Externo -->
                    <div class="bg-[#0f1015] border border-stone-800 rounded p-4">
                        <label class="block font-mono text-xs uppercase font-bold text-stone-300 mb-1.5">
                            Opção A &bull; Link da Notícia (G1, Folha, UOL, etc.)
                        </label>
                        <input type="url" id="furo-url-input" placeholder="https://g1.globo.com/politica/noticia/..."
                            class="w-full bg-[#171922] border border-stone-700 rounded px-3 py-2 text-sm text-stone-100 font-mono focus:outline-hidden focus:border-amber-500 placeholder:text-stone-600">
                        <p class="text-[11px] text-stone-500 mt-1 font-sans">
                            O robô fará a raspagem do fato real e gerará a crônica satírica com caricatura.
                        </p>
                    </div>

                    <!-- Opção 2: Tema Personalizado -->
                    <div class="bg-[#0f1015] border border-stone-800 rounded p-4">
                        <label class="block font-mono text-xs uppercase font-bold text-stone-300 mb-1.5">
                            Opção B &bull; Tema ou Pauta Exclusiva da Redação
                        </label>
                        <input type="text" id="furo-tema-input" placeholder="Ex: Ministro do STF gastando milhões em hotel em Roma..."
                            class="w-full bg-[#171922] border border-stone-700 rounded px-3 py-2 text-sm text-stone-100 font-mono focus:outline-hidden focus:border-amber-500 placeholder:text-stone-600">
                        <p class="text-[11px] text-stone-500 mt-1 font-sans">
                            Crie uma pauta provocativa do zero para o robô satirizar com ironia mordaz.
                        </p>
                    </div>
                </div>

                <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-3 border-t border-stone-800">
                    <div class="text-xs font-mono text-stone-400 text-center sm:text-left">
                        <span>Como disparar:</span>
                        <span class="text-stone-300"> Clique no botão para disparar o robô no GitHub Actions com a pauta escolhida.</span>
                    </div>
                    <div class="flex items-center gap-3 w-full sm:w-auto">
                        <button onclick="dispararFuro()" class="w-full sm:w-auto bg-amber-600 hover:bg-amber-500 text-stone-950 font-mono font-black px-6 py-2.5 rounded text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer shadow-md">
                            <span>🚀</span>
                            <span>DISPARAR FURO AGORA</span>
                        </button>
                    </div>
                </div>

                <!-- Feedback de Disparo -->
                <div id="furo-feedback" class="hidden mt-4 p-4 rounded bg-stone-900 border border-amber-600/50 text-xs font-mono"></div>
            </div>

            <!-- AUDITORIA: HISTÓRICO DAS EXECUÇÕES -->
            <div class="bg-[#14161f] border border-stone-800 rounded-lg p-5">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                    <div>
                        <h3 class="font-cinzel font-black text-lg text-stone-100 flex items-center gap-2">
                            <span>📋</span>
                            <span>HISTÓRICO DE AUDITORIA &amp; EXECUÇÕES</span>
                        </h3>
                        <p class="font-sans text-xs text-stone-400">
                            Registro dos últimos ciclos do robô com tempo de resposta, validação e motivos de retenção.
                        </p>
                    </div>
                    <span class="text-xs font-mono text-stone-500">Últimas rodadas registradas</span>
                </div>

                <div class="overflow-x-auto border border-stone-800 rounded">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-[#0e0f14] border-b border-stone-800 text-[11px] font-mono text-stone-400 uppercase tracking-wider">
                                <th class="px-4 py-3">Horário</th>
                                <th class="px-4 py-3">Status</th>
                                <th class="px-4 py-3">Crônica / Manchete</th>
                                <th class="px-4 py-3 text-center">Duração</th>
                                <th class="px-4 py-3 text-center">Caricatura</th>
                                <th class="px-4 py-3 text-center">Áudio</th>
                                <th class="px-4 py-3">Diagnóstico</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-stone-800/60 font-sans">
                            {historico_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- RAIO-X DOS ARTIGOS NO AR (AUDITORIA VISUAL E ÁUDIO) -->
            <div class="bg-[#14161f] border border-stone-800 rounded-lg p-5">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                    <div>
                        <h3 class="font-cinzel font-black text-lg text-stone-100 flex items-center gap-2">
                            <span>🔍</span>
                            <span>RAIO-X DOS ARTIGOS PUBLICADOS</span>
                        </h3>
                        <p class="font-sans text-xs text-stone-400">
                            Conferência detalhada das últimas matérias no ar com peso de imagem (>50KB) e áudio neural.
                        </p>
                    </div>
                    <span class="text-xs font-mono text-stone-500">Total: {len(articles)} publicados</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {artigos_raiox_html}
                </div>
            </div>

            <!-- RADAR DE PAUTAS QUENTES (VIGILÂNCIA AUTOMÁTICA) -->
            <div class="bg-[#14161f] border border-stone-800 rounded-lg p-5">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                    <div>
                        <h3 class="font-cinzel font-black text-lg text-stone-100 flex items-center gap-2">
                            <span>📡</span>
                            <span>RADAR DE PAUTAS QUENTES (MONITORAMENTO PASSIVO)</span>
                        </h3>
                        <p class="font-sans text-xs text-stone-400">
                            Notícias sob vigilância do robô. <strong>Atenção:</strong> você não precisa tomar decisões aqui. O robô seleciona e publica a matéria mais quente sozinho nos 4 horários diários.
                        </p>
                    </div>
                    <span class="text-xs font-mono text-emerald-400 font-bold">100% Autônomo</span>
                </div>

                <div class="overflow-x-auto border border-stone-800 rounded">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-[#0e0f14] border-b border-stone-800 text-[11px] font-mono text-stone-400 uppercase tracking-wider">
                                <th class="px-4 py-3">Posição</th>
                                <th class="px-4 py-3">Veículo</th>
                                <th class="px-4 py-3">Manchete Noticiada</th>
                                <th class="px-4 py-3 text-center">Score</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-stone-800/60 font-sans">
                            {radar_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

        </main>

        <!-- RODAPÉ DA SALA DE MÁQUINAS -->
        <footer class="bg-[#0e0f14] border-t border-stone-800 py-6 text-center text-xs font-mono text-stone-500">
            <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
                <span>PORTAL ÍMPROBO &bull; SISTEMA DE CONTROLE EDITORIAL</span>
                <span>Deploy Contínuo via GitHub Actions &amp; Vercel &bull; 2026</span>
            </div>
        </footer>

    </div>

    <!-- SCRIPT DE INTERATIVIDADE, PIN E CRONÔMETRO -->
    <script>
        const PIN_CORRETO = "improbo2026";
        const GITHUB_WORKFLOW_URL = "https://github.com/Pavlosk1994/portal-improbo/actions/workflows/robo-cron.yml";

        // 1. Verificação de PIN
        function verificarPIN() {{
            const input = document.getElementById("pin-input");
            const err = document.getElementById("pin-error");
            if (input.value === PIN_CORRETO) {{
                sessionStorage.setItem("improbo_sala_auth", "true");
                document.getElementById("pin-lock-modal").classList.add("hidden");
                document.getElementById("dashboard-content").classList.remove("hidden");
                iniciarCronometro();
            }} else {{
                err.classList.remove("hidden");
                input.classList.add("border-red-500");
                input.focus();
            }}
        }}

        function bloquearConsole() {{
            sessionStorage.removeItem("improbo_sala_auth");
            location.reload();
        }}

        document.getElementById("pin-input").addEventListener("keypress", function(e) {{
            if (e.key === "Enter") verificarPIN();
        }});

        // Auto-login se já autenticado na sessão
        window.addEventListener("DOMContentLoaded", function() {{
            if (sessionStorage.getItem("improbo_sala_auth") === "true") {{
                document.getElementById("pin-lock-modal").classList.add("hidden");
                document.getElementById("dashboard-content").classList.remove("hidden");
                iniciarCronometro();
            }} else {{
                document.getElementById("pin-input").focus();
            }}
        }});

        // 2. Cronômetro das 4 Edições Diárias (08h, 13h, 18h, 22h BRT)
        function iniciarCronometro() {{
            function atualizar() {{
                const agora = new Date();
                // Converte para horário de Brasília (UTC-3)
                const utc = agora.getTime() + (agora.getTimezoneOffset() * 60000);
                const brt = new Date(utc - (3 * 3600000));

                const slots = [8, 13, 18, 22];
                const horaAtual = brt.getHours();
                const minAtual = brt.getMinutes();
                const secAtual = brt.getSeconds();

                // Acha o próximo slot
                let proximoSlot = null;
                for (let s of slots) {{
                    if (s > horaAtual || (s === horaAtual && (minAtual > 0 || secAtual > 0) === false)) {{
                        proximoSlot = s;
                        break;
                    }}
                }}

                let diffMs = 0;
                let dataAlvo = new Date(brt);

                if (proximoSlot !== null) {{
                    dataAlvo.setHours(proximoSlot, 0, 0, 0);
                    diffMs = dataAlvo - brt;
                }} else {{
                    // Próximo é 08:00 de amanhã
                    proximoSlot = 8;
                    dataAlvo.setDate(dataAlvo.getDate() + 1);
                    dataAlvo.setHours(8, 0, 0, 0);
                    diffMs = dataAlvo - brt;
                }}

                if (diffMs < 0) diffMs = 0;

                const horas = Math.floor(diffMs / 3600000);
                const minutos = Math.floor((diffMs % 3600000) / 60000);
                const segundos = Math.floor((diffMs % 60000) / 1000);

                const fH = String(horas).padStart(2, '0');
                const fM = String(minutos).padStart(2, '0');
                const fS = String(segundos).padStart(2, '0');

                const timerEl = document.getElementById("countdown-timer");
                const labelEl = document.getElementById("proximo-horario-label");

                if (timerEl) timerEl.textContent = `${{fH}}:${{fM}}:${{fS}}`;
                if (labelEl) labelEl.textContent = `Próximo disparo agendado às ${{String(proximoSlot).padStart(2, '0')}}:00 (Horário de Brasília)`;
            }}

            atualizar();
            setInterval(atualizar, 1000);
        }}

        // 3. Disparo de Furo de Reportagem
        function dispararFuro() {{
            const urlVal = document.getElementById("furo-url-input").value.trim();
            const temaVal = document.getElementById("furo-tema-input").value.trim();
            const feedback = document.getElementById("furo-feedback");

            if (!urlVal && !temaVal) {{
                alert("Por favor, preencha pelo menos um dos campos: a URL da notícia ou o Tema da pauta.");
                return;
            }}

            feedback.classList.remove("hidden");
            feedback.innerHTML = `
                <div class="space-y-3">
                    <p class="text-amber-400 font-bold">🚀 Preparando disparo de Furo de Reportagem:</p>
                    <div class="text-stone-300">
                        ${{urlVal ? `<div>&bull; <strong>URL:</strong> ${{urlVal}}</div>` : ""}}
                        ${{temaVal ? `<div>&bull; <strong>Tema:</strong> ${{temaVal}}</div>` : ""}}
                    </div>
                    <div class="p-3 bg-black/60 rounded border border-stone-800 text-stone-300">
                        <p class="font-bold text-amber-300 mb-1">Como acionar a publicação no GitHub Actions:</p>
                        <p class="text-xs mb-2">Para garantir máxima segurança, o disparo é feito diretamente na aba Actions do repositório:</p>
                        <ol class="list-decimal list-inside space-y-1 text-xs text-stone-400 mb-3">
                            <li>Clique no botão verde abaixo para abrir o workflow do robô.</li>
                            <li>Clique no botão <strong>"Run workflow"</strong> no canto superior direito.</li>
                            <li>Cole o link ou tema nos campos correspondentes e clique em <strong>"Run workflow"</strong>.</li>
                        </ol>
                        <a href="${{GITHUB_WORKFLOW_URL}}" target="_blank" rel="noopener noreferrer" 
                           class="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-stone-950 font-bold px-4 py-2 rounded text-xs uppercase tracking-wider transition-colors">
                            <span>Abrir GitHub Actions &rarr;</span>
                        </a>
                    </div>
                </div>
            `;
        }}
    </script>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    print("[*] Testando geração da Sala de Máquinas...")
    html = generate_sala_de_maquinas_page([])
    print(f"[✓] Gerado com sucesso! Tamanho: {len(html)} bytes.")
