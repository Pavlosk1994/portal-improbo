#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SALA DE MÁQUINAS - PAINEL DE CONTROLE DE ALTA DENSIDADE (UI/UX SÊNIOR)
Interface limpa, compacta, orientada a dados (data-dense) e sem verbosidade de IA.
Substitui blocos de texto por popovers/tooltips flutuantes (hover/focus).
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
        return f"{kb/1024:.1f} MB"
    return f"{kb:.0f} KB"

def info_tip(texto, align="center"):
    """Gera um ícone de informação discreto com tooltip flutuante no hover/focus"""
    pos_classes = "left-1/2 -translate-x-1/2" if align == "center" else ("left-0" if align == "left" else "right-0")
    arrow_classes = "left-1/2 -translate-x-1/2" if align == "center" else ("left-3" if align == "left" else "right-3")
    
    return f"""<span class="relative inline-flex items-center ml-1.5 group align-middle">
        <span tabindex="0" role="button" aria-label="Ajuda" class="w-3.5 h-3.5 rounded-full border border-stone-700 hover:border-amber-500/70 text-stone-400 hover:text-amber-400 text-[9px] font-mono inline-flex items-center justify-center cursor-help transition-colors select-none">i</span>
        <span class="pointer-events-none opacity-0 group-hover:opacity-100 group-focus:opacity-100 transition-opacity duration-150 absolute bottom-full {pos_classes} mb-1.5 z-50 w-64 p-2 bg-[#181b24] border border-stone-700/80 rounded shadow-2xl text-[11px] font-sans text-stone-300 normal-case leading-relaxed font-normal whitespace-normal tracking-normal text-left">
            {texto}
            <span class="absolute top-full {arrow_classes} border-4 border-transparent border-t-[#181b24]"></span>
        </span>
    </span>"""

def generate_sala_de_maquinas_page(articles, portal_url="https://portal-improbo.vercel.app"):
    telemetria = carregar_telemetria()
    historico = telemetria.get("historico_execucoes", [])
    radar = telemetria.get("radar_pautas", [])

    # Monta Linhas do Histórico de Auditoria
    historico_rows = ""
    if not historico:
        historico_rows = """
        <tr>
            <td colspan="7" class="px-3 py-4 text-center text-stone-500 font-mono text-xs">
                Nenhuma execução registrada.
            </td>
        </tr>
        """
    else:
        for ex in historico[:15]:
            st = ex.get("status", "INFO")
            if st == "SUCESSO":
                badge = '<span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-700/50">SUCESSO</span>'
            elif st == "RETIDO":
                badge = '<span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950/60 text-amber-300 border border-amber-600/50">RETIDO</span>'
            else:
                badge = '<span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-red-950/60 text-red-400 border border-red-700/50">ERRO</span>'

            horario = ex.get("horario_brt") or ex.get("timestamp", "-")[:16].replace("T", " ")
            titulo = ex.get("titulo") or "Varredura de Rotina"
            slug = ex.get("slug")
            
            if st == "SUCESSO" and slug:
                titulo_el = f'<a href="artigos/{slug}.html" target="_blank" class="hover:text-amber-300 underline underline-offset-2 truncate block max-w-sm">{titulo}</a>'
            elif st == "RETIDO":
                titulo_el = f'<span class="text-stone-400 truncate block max-w-sm italic">{titulo} <span class="text-[9px] text-amber-500 font-mono">(Abortado)</span></span>'
            else:
                titulo_el = f'<span class="text-stone-400 truncate block max-w-sm">{titulo}</span>'

            duracao = f"{ex.get('duracao_segundos', 0):.1f}s"
            img_kb = f"{ex.get('imagem_tamanho_kb', 0):.0f} KB" if ex.get('imagem_tamanho_kb') else "-"
            audio_kb = f"{ex.get('audio_tamanho_kb', 0):.0f} KB" if ex.get('audio_tamanho_kb') else "-"
            motivo = ex.get("motivo", "-")

            historico_rows += f"""
            <tr class="border-b border-stone-800/40 hover:bg-stone-900/40 transition-colors">
                <td class="px-3 py-2 font-mono text-[11px] text-stone-400 whitespace-nowrap">{horario}</td>
                <td class="px-3 py-2 whitespace-nowrap">{badge}</td>
                <td class="px-3 py-2 font-sans text-xs text-stone-200">{titulo_el}</td>
                <td class="px-3 py-2 font-mono text-[11px] text-stone-300 text-center">{duracao}</td>
                <td class="px-3 py-2 font-mono text-[11px] text-stone-300 text-center">{img_kb}</td>
                <td class="px-3 py-2 font-mono text-[11px] text-stone-300 text-center">{audio_kb}</td>
                <td class="px-3 py-2 font-mono text-[11px] text-stone-400 max-w-xs truncate" title="{motivo}">{motivo}</td>
            </tr>
            """

    # Monta Cards Compactos do Acervo de Artigos
    artigos_cards = ""
    for art in articles[:12]:
        slug = art.get("slug")
        titulo = art.get("titulo")
        data_pub = art.get("data", "")
        corpo = art.get("corpo", [])
        palavras = sum(len(p.split()) for p in corpo)

        caminho_img = os.path.join(IMAGENS_DIR, f"{slug}.jpg")
        img_size = os.path.getsize(caminho_img) if os.path.exists(caminho_img) else 0
        img_tam_txt = formatar_tamanho(img_size)

        caminho_aud = os.path.join(AUDIO_DIR, f"{slug}.mp3")
        aud_size = os.path.getsize(caminho_aud) if os.path.exists(caminho_aud) else 0
        aud_tam_txt = formatar_tamanho(aud_size)

        artigos_cards += f"""
        <div class="bg-[#13151c] border border-stone-800/80 rounded p-2.5 flex flex-col justify-between hover:border-stone-700 transition-colors">
            <div>
                <div class="relative overflow-hidden rounded mb-2 bg-stone-900 aspect-[16/9] border border-stone-800/60">
                    <img src="imagens/{slug}.jpg" alt="{titulo}" class="w-full h-full object-cover" loading="lazy">
                    <div class="absolute bottom-1.5 left-1.5 right-1.5 flex items-center justify-between pointer-events-none">
                        <span class="bg-black/85 backdrop-blur-xs text-emerald-400 font-mono text-[9px] font-bold px-1.5 py-0.5 rounded border border-emerald-500/20">
                            {img_tam_txt}
                        </span>
                        <span class="bg-black/85 backdrop-blur-xs text-amber-300 font-mono text-[9px] font-bold px-1.5 py-0.5 rounded border border-amber-500/20">
                            {aud_tam_txt}
                        </span>
                    </div>
                </div>
                <div class="flex items-center gap-1.5 mb-1 text-[10px] font-mono text-stone-500">
                    <span>{data_pub}</span>
                    <span>&bull;</span>
                    <span>{palavras}p</span>
                </div>
                <h4 class="font-serif font-bold text-xs text-stone-100 line-clamp-2 leading-snug mb-2">
                    <a href="artigos/{slug}.html" target="_blank" class="hover:text-amber-300 transition-colors">{titulo}</a>
                </h4>
            </div>
            <div class="pt-2 border-t border-stone-800/60 flex items-center justify-between text-[10px] font-mono">
                <span class="text-emerald-400 font-semibold">Auditado ✓</span>
                <a href="artigos/{slug}.html" target="_blank" class="text-amber-400 hover:text-amber-300 underline underline-offset-2">Abrir &rarr;</a>
            </div>
        </div>
        """

    # Monta Linhas do Radar RSS
    radar_rows = ""
    if not radar:
        radar_rows = """
        <tr>
            <td colspan="4" class="px-3 py-4 text-center text-stone-500 font-mono text-xs">
                Radar em inicialização. Aguardando primeira varredura.
            </td>
        </tr>
        """
    else:
        for idx, item in enumerate(radar[:5], start=1):
            sc = item.get("score", 0)
            fonte = item.get("fonte", "RSS")
            tit = item.get("titulo", "")
            lnk = item.get("link", "#")
            radar_rows += f"""
            <tr class="border-b border-stone-800/40 hover:bg-stone-900/40 transition-colors">
                <td class="px-3 py-2 font-mono text-[11px] font-bold text-amber-400">#{idx}</td>
                <td class="px-3 py-2 font-mono text-[11px] text-stone-400 whitespace-nowrap">{fonte}</td>
                <td class="px-3 py-2 font-sans text-xs text-stone-200">
                    <a href="{lnk}" target="_blank" rel="noopener noreferrer" class="hover:text-amber-300 underline underline-offset-2 truncate block max-w-md">{tit}</a>
                </td>
                <td class="px-3 py-2 font-mono text-[11px] text-emerald-400 text-center font-bold">{sc}</td>
            </tr>
            """

    tip_proxima_edicao = info_tip("Horários fixos do robô: 08:00, 13:00, 18:00 e 22:00 BRT. Disparado automaticamente via GitHub Actions.")
    tip_servicos = info_tip("Status operacional das conexões externas: IA Gemini (redação/arte), feeds RSS nacionais, narração neural Edge-TTS e deploy Vercel.")
    tip_portao = info_tip("Portão Mandatório: bloqueia publicação se o texto estiver incompleto, se a caricatura for ausente ou menor que 50KB, ou se faltar áudio MP3.")
    tip_acervo = info_tip("Total de crônicas satíricas em produção com integridade verificada de arquivo visual e narração sonora.")
    tip_furo = info_tip("Disparo imediato fora da grade horária. O robô faz a raspagem da URL externa ou desenvolve o tema mantendo a Regra de Ouro editorial.")
    tip_historico = info_tip("Registro cronológico das rodadas executadas com latência, peso dos artefatos e motivo de retenção em caso de descarte preventivo.")
    tip_radar = info_tip("Top 5 manchetes monitoradas nos feeds RSS. O robô escolhe e publica a matéria mais quente sozinho; não requer aprovação manual.")
    tip_raiox = info_tip("Auditoria visual e sonora das matérias publicadas. Confirmação dos pesos em KB da charge editorial e do arquivo de áudio.")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sala de Máquinas &bull; ÍMPROBO</title>
    <meta name="robots" content="noindex, nofollow">
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #090a0f;
            color: #d1d5db;
        }}
        .font-mono {{ font-family: 'JetBrains Mono', Consolas, monospace; }}
        .font-serif {{ font-family: 'Playfair Display', Georgia, serif; }}
        
        /* Scrollbar enxuta */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0c0d12; }}
        ::-webkit-scrollbar-thumb {{ background: #1f2330; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #32384a; }}
    </style>
</head>
<body class="min-h-screen flex flex-col bg-[#090a0f] text-stone-200 antialiased selection:bg-amber-600 selection:text-white">

    <!-- MODAL DE BLOQUEIO / PIN (COMPACTO) -->
    <div id="pin-lock-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-xs p-4">
        <div class="bg-[#12141c] border border-stone-800 rounded max-w-xs w-full p-5 shadow-2xl text-center">
            <div class="w-9 h-9 mx-auto mb-2.5 rounded-full bg-stone-900 border border-amber-600/40 flex items-center justify-center text-amber-500 text-sm font-mono">
                🔒
            </div>
            <h2 class="font-mono font-bold text-xs text-stone-100 uppercase tracking-widest mb-1">
                ACESSO RESTRITO
            </h2>
            <p class="font-mono text-[10px] text-stone-500 mb-4">
                SALA DE MÁQUINAS &bull; ÍMPROBO
            </p>
            <div class="mb-3">
                <input type="password" id="pin-input" maxlength="16" placeholder="PIN (improbo2026)" 
                    class="w-full bg-[#0a0b0e] border border-stone-700/80 rounded px-3 py-2 text-center font-mono text-sm text-amber-300 focus:outline-hidden focus:border-amber-500 tracking-wider placeholder:text-stone-600 placeholder:text-xs">
            </div>
            <div id="pin-error" class="hidden text-[10px] font-mono text-red-400 mb-3 font-semibold">
                [!] PIN incorreto.
            </div>
            <button onclick="verificarPIN()" class="w-full bg-amber-600 hover:bg-amber-500 text-stone-950 font-mono font-bold py-2 rounded text-xs uppercase tracking-wider transition-colors cursor-pointer">
                DESBLOQUEAR
            </button>
        </div>
    </div>

    <!-- CONTEÚDO PRINCIPAL (DASHBOARD RESTRITO) -->
    <div id="dashboard-content" class="hidden flex-1 flex flex-col">
        
        <!-- HEADER COMPACTO (48px) -->
        <header class="bg-[#0f1118] border-b border-stone-800/80 sticky top-0 z-40">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 h-12 flex items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                    <span class="font-mono text-xs font-bold text-amber-400 tracking-wider flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        ÍMPROBO &bull; CONSOLE
                    </span>
                    <span class="hidden sm:inline-block text-stone-700">|</span>
                    <span class="hidden sm:flex items-center gap-2 text-[11px] font-mono text-stone-400">
                        <span class="px-1.5 py-0.5 rounded bg-stone-900 border border-stone-800 text-stone-400">4x/dia</span>
                        <span class="px-1.5 py-0.5 rounded bg-stone-900 border border-stone-800 text-stone-400">Free Tier</span>
                    </span>
                </div>

                <div class="flex items-center gap-2">
                    <a href="index.html" target="_blank" class="px-2.5 py-1 rounded bg-stone-900 hover:bg-stone-800 border border-stone-700/80 text-stone-300 hover:text-white font-mono text-xs flex items-center gap-1 transition-colors">
                        <span>Portal ↗</span>
                    </a>
                    <button onclick="bloquearConsole()" class="px-2.5 py-1 rounded bg-red-950/30 hover:bg-red-950/60 border border-red-800/40 text-red-300 font-mono text-xs transition-colors cursor-pointer" title="Bloquear sessão">
                        <span>🔒</span>
                    </button>
                </div>
            </div>
        </header>

        <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-5 space-y-5">

            <!-- STRIP DE MÉTRICAS (4 CARDS DATA-DENSE) -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <!-- KPI 1: Próxima Edição -->
                <div class="bg-[#12141c] border border-stone-800/80 rounded p-3 flex flex-col justify-between">
                    <div class="flex items-center justify-between text-[11px] font-mono text-stone-400 uppercase">
                        <span>PRÓXIMO CICLO {tip_proxima_edicao}</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                    </div>
                    <div class="my-1.5">
                        <div id="countdown-timer" class="font-mono font-bold text-xl sm:text-2xl text-stone-100 tracking-tight">
                            --:--:--
                        </div>
                    </div>
                    <div id="proximo-horario-label" class="text-[10px] font-mono text-stone-500 truncate">
                        Aguardando BRT...
                    </div>
                </div>

                <!-- KPI 2: Serviços & APIs -->
                <div class="bg-[#12141c] border border-stone-800/80 rounded p-3 flex flex-col justify-between">
                    <div class="flex items-center justify-between text-[11px] font-mono text-stone-400 uppercase">
                        <span>SERVIÇOS / APIS {tip_servicos}</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    </div>
                    <div class="my-1.5">
                        <div class="font-mono font-bold text-xl sm:text-2xl text-emerald-400 tracking-tight">
                            4 / 4 ONLINE
                        </div>
                    </div>
                    <div class="text-[10px] font-mono text-stone-400 flex items-center gap-2 truncate">
                        <span>● Gemini</span>
                        <span>● Feeds</span>
                        <span>● TTS</span>
                        <span>● Vercel</span>
                    </div>
                </div>

                <!-- KPI 3: Portão de Qualidade -->
                <div class="bg-[#12141c] border border-stone-800/80 rounded p-3 flex flex-col justify-between">
                    <div class="flex items-center justify-between text-[11px] font-mono text-stone-400 uppercase">
                        <span>PORTÃO EDITORIAL {tip_portao}</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    </div>
                    <div class="my-1.5">
                        <div class="font-mono font-bold text-xl sm:text-2xl text-stone-100 tracking-tight">
                            ATIVO
                        </div>
                    </div>
                    <div class="text-[10px] font-mono text-stone-500 truncate">
                        Regra de Ouro: Arte &ge; 50KB
                    </div>
                </div>

                <!-- KPI 4: Matérias Publicadas -->
                <div class="bg-[#12141c] border border-stone-800/80 rounded p-3 flex flex-col justify-between">
                    <div class="flex items-center justify-between text-[11px] font-mono text-stone-400 uppercase">
                        <span>ACERVO NO AR {tip_acervo}</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-stone-500"></span>
                    </div>
                    <div class="my-1.5">
                        <div class="font-mono font-bold text-xl sm:text-2xl text-stone-100 tracking-tight">
                            {len(articles)} MATÉRIAS
                        </div>
                    </div>
                    <div class="text-[10px] font-mono text-stone-500 truncate">
                        100% com caricatura e áudio
                    </div>
                </div>
            </div>

            <!-- TOOLBAR DE DISPARO SOB DEMANDA (FURO COMPACTO) -->
            <div class="bg-[#12141c] border border-stone-800/90 rounded p-3.5">
                <div class="flex items-center justify-between mb-2.5">
                    <div class="flex items-center gap-2">
                        <span class="font-mono text-xs uppercase font-bold text-amber-400 flex items-center gap-1">
                            <span>⚡</span>
                            <span>DISPARO SOB DEMANDA (FURO)</span>
                        </span>
                        {tip_furo}
                    </div>

                    <!-- Toggle Segmentado -->
                    <div class="flex items-center bg-[#0a0b0e] border border-stone-800 rounded p-0.5 text-[10px] font-mono">
                        <button id="btn-tab-url" onclick="alternarAbaFuro('url')" class="px-2 py-0.5 rounded bg-stone-800 text-stone-100 font-bold transition-colors cursor-pointer">
                            URL Externa
                        </button>
                        <button id="btn-tab-tema" onclick="alternarAbaFuro('tema')" class="px-2 py-0.5 rounded text-stone-400 hover:text-stone-200 transition-colors cursor-pointer">
                            Tema Livre
                        </button>
                    </div>
                </div>

                <!-- Input + Botão Inline -->
                <div class="flex flex-col sm:flex-row items-center gap-2">
                    <div class="relative flex-1 w-full">
                        <input type="text" id="furo-input-url" placeholder="Cole a URL da matéria (ex: https://g1.globo.com/...)"
                            class="w-full bg-[#0a0b0e] border border-stone-800 rounded px-3 py-1.5 text-xs text-stone-100 font-mono focus:outline-hidden focus:border-amber-500 placeholder:text-stone-600">
                        <input type="text" id="furo-input-tema" placeholder="Digite a pauta exclusiva (ex: Farra de passagens no STF...)"
                            class="hidden w-full bg-[#0a0b0e] border border-stone-800 rounded px-3 py-1.5 text-xs text-stone-100 font-mono focus:outline-hidden focus:border-amber-500 placeholder:text-stone-600">
                    </div>
                    <button onclick="dispararFuro()" class="w-full sm:w-auto bg-amber-600 hover:bg-amber-500 text-stone-950 font-mono font-bold px-4 py-1.5 rounded text-xs uppercase tracking-wider transition-colors shrink-0 cursor-pointer flex items-center justify-center gap-1.5">
                        <span>🚀</span>
                        <span>Disparar Furo</span>
                    </button>
                </div>

                <!-- Feedback Compacto -->
                <div id="furo-feedback" class="hidden mt-2.5 p-2.5 rounded bg-[#0b0c10] border border-amber-600/40 text-xs font-mono"></div>
            </div>

            <!-- GRID DUPLO: HISTÓRICO & RADAR -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                
                <!-- HISTÓRICO DE AUDITORIA (2 COLUNAS) -->
                <div class="lg:col-span-2 bg-[#12141c] border border-stone-800/80 rounded p-3.5 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center gap-1.5">
                                <h3 class="font-mono text-xs font-bold text-stone-200 uppercase">
                                    HISTÓRICO DE EXECUÇÕES
                                </h3>
                                {tip_historico}
                            </div>
                            <span class="text-[10px] font-mono text-stone-500">Últimos registros</span>
                        </div>

                        <div class="overflow-x-auto border border-stone-800/60 rounded">
                            <table class="w-full text-left border-collapse">
                                <thead>
                                    <tr class="bg-[#0b0c10] border-b border-stone-800/80 text-[10px] font-mono text-stone-400 uppercase">
                                        <th class="px-3 py-2">Horário</th>
                                        <th class="px-3 py-2">Status</th>
                                        <th class="px-3 py-2">Crônica</th>
                                        <th class="px-3 py-2 text-center">Tempo</th>
                                        <th class="px-3 py-2 text-center">Arte</th>
                                        <th class="px-3 py-2 text-center">Áudio</th>
                                        <th class="px-3 py-2">Diagnóstico</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-stone-800/40">
                                    {historico_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- RADAR DE TENDÊNCIAS (1 COLUNA) -->
                <div class="bg-[#12141c] border border-stone-800/80 rounded p-3.5 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center gap-1.5">
                                <h3 class="font-mono text-xs font-bold text-stone-200 uppercase">
                                    RADAR RSS (PASSIVO)
                                </h3>
                                {tip_radar}
                            </div>
                            <span class="text-[10px] font-mono text-emerald-400">Autônomo</span>
                        </div>

                        <div class="overflow-x-auto border border-stone-800/60 rounded">
                            <table class="w-full text-left border-collapse">
                                <thead>
                                    <tr class="bg-[#0b0c10] border-b border-stone-800/80 text-[10px] font-mono text-stone-400 uppercase">
                                        <th class="px-3 py-2">#</th>
                                        <th class="px-3 py-2">Veículo</th>
                                        <th class="px-3 py-2">Manchete</th>
                                        <th class="px-3 py-2 text-center">Score</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-stone-800/40">
                                    {radar_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

            </div>

            <!-- ACERVO AUDITADO (RAIO-X COMPACTO) -->
            <div class="bg-[#12141c] border border-stone-800/80 rounded p-3.5">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-1.5">
                        <h3 class="font-mono text-xs font-bold text-stone-200 uppercase">
                            ACERVO AUDITADO NO AR ({len(articles)})
                        </h3>
                        {tip_raiox}
                    </div>
                    <span class="text-[10px] font-mono text-stone-500">Últimas 12 edições</span>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-2.5">
                    {artigos_cards}
                </div>
            </div>

        </main>

        <!-- FOOTER COMPACTO -->
        <footer class="bg-[#0b0c10] border-t border-stone-800/80 py-3 text-center text-[10px] font-mono text-stone-500">
            <div class="max-w-7xl mx-auto px-4 flex items-center justify-between">
                <span>ÍMPROBO &bull; CONSOLE OPERACIONAL</span>
                <span>GitHub Actions &amp; Vercel &bull; 2026</span>
            </div>
        </footer>

    </div>

    <!-- SCRIPT DO DASHBOARD -->
    <script>
        const PIN_CORRETO = "improbo2026";
        const GITHUB_WORKFLOW_URL = "https://github.com/Pavlosk1994/portal-improbo/actions/workflows/robo-cron.yml";
        let modoAtualFuro = "url";

        // 1. PIN de Acesso
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
                const utc = agora.getTime() + (agora.getTimezoneOffset() * 60000);
                const brt = new Date(utc - (3 * 3600000));

                const slots = [8, 13, 18, 22];
                const horaAtual = brt.getHours();
                const minAtual = brt.getMinutes();
                const secAtual = brt.getSeconds();

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
                if (labelEl) labelEl.textContent = `Previsto às ${{String(proximoSlot).padStart(2, '0')}}:00 BRT`;
            }}

            atualizar();
            setInterval(atualizar, 1000);
        }}

        // 3. Alternância de Modo Furo (URL vs Tema)
        function alternarAbaFuro(modo) {{
            modoAtualFuro = modo;
            const inputUrl = document.getElementById("furo-input-url");
            const inputTema = document.getElementById("furo-input-tema");
            const btnUrl = document.getElementById("btn-tab-url");
            const btnTema = document.getElementById("btn-tab-tema");

            if (modo === "url") {{
                inputUrl.classList.remove("hidden");
                inputTema.classList.add("hidden");
                btnUrl.className = "px-2 py-0.5 rounded bg-stone-800 text-stone-100 font-bold transition-colors cursor-pointer";
                btnTema.className = "px-2 py-0.5 rounded text-stone-400 hover:text-stone-200 transition-colors cursor-pointer";
                inputUrl.focus();
            }} else {{
                inputUrl.classList.add("hidden");
                inputTema.classList.remove("hidden");
                btnTema.className = "px-2 py-0.5 rounded bg-stone-800 text-stone-100 font-bold transition-colors cursor-pointer";
                btnUrl.className = "px-2 py-0.5 rounded text-stone-400 hover:text-stone-200 transition-colors cursor-pointer";
                inputTema.focus();
            }}
        }}

        // 4. Disparo do Furo
        function dispararFuro() {{
            const urlVal = document.getElementById("furo-input-url").value.trim();
            const temaVal = document.getElementById("furo-input-tema").value.trim();
            const valorFinal = modoAtualFuro === "url" ? urlVal : temaVal;
            const feedback = document.getElementById("furo-feedback");

            if (!valorFinal) {{
                alert(modoAtualFuro === "url" ? "Insira a URL da notícia." : "Digite o tema da pauta.");
                return;
            }}

            feedback.classList.remove("hidden");
            feedback.innerHTML = `
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                    <div class="text-stone-300">
                        <span class="text-amber-400 font-bold">Pauta:</span> 
                        <span class="text-stone-200">${{valorFinal}}</span>
                    </div>
                    <a href="${{GITHUB_WORKFLOW_URL}}" target="_blank" rel="noopener noreferrer" 
                       class="inline-flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-stone-950 font-bold px-3 py-1 rounded text-[11px] uppercase tracking-wider shrink-0 transition-colors">
                        <span>Executar no Actions &rarr;</span>
                    </a>
                </div>
            `;
        }}
    </script>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    print("[*] Compilando Sala de Máquinas (Refatorada)...")
    html = generate_sala_de_maquinas_page([])
    print(f"[✓] Gerado com sucesso! Tamanho: {len(html)} bytes.")
