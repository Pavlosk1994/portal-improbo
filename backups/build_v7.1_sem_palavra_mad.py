#!/usr/bin/env python3
"""
Gerador de Site Estático - IMPRÓBO (Estética New York Times & Papel Creme)
Fundo papel creme (#F4F1EA), container do artigo em branco puro (#FFFFFF), 
linhas editoriais clássicas com borda dupla (#121212), divisores em #D1CEC7
e caixas factuais em #EBE7DE com borda grossa.
"""

import os
import json
import glob
from datetime import datetime

PORTAL_NAME = "IMPRÓBO"
PORTAL_SLOGAN = "A crônica semanal da falta de decoro e do absurdo nacional."
INSTAGRAM_URL = "https://instagram.com"
INSTAGRAM_HANDLE = "@improbo"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
ARTIGOS_DIR = os.path.join(BASE_DIR, "artigos")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
VERCEL_JSON_PATH = os.path.join(BASE_DIR, "vercel.json")

COMMON_HEAD_STYLES = """
    <meta name="referrer" content="no-referrer">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,800;1,6..72,400;1,6..72,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-nyt: #F4F1EA;
            --container-white: #FFFFFF;
            --text-charcoal: #121212;
            --editorial-red: #8B0000;
            --border-divider: #D1CEC7;
            --box-cream-dark: #EBE7DE;
        }

        body {
            background-color: var(--bg-nyt);
            color: var(--text-charcoal);
            font-family: 'Newsreader', Georgia, serif;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
        }

        .font-sans {
            font-family: 'Inter', system-ui, sans-serif;
        }

        /* Linhas Editoriais Clássicas New York Times */
        .masthead-borders {
            border-top: 1px solid #121212;
            border-bottom: 3px double #121212;
        }

        .editorial-divider {
            border-color: #D1CEC7;
        }

        /* Tipografia Fluida Responsiva com clamp() */
        .masthead-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: clamp(2.3rem, 7.5vw, 4.8rem);
            line-height: 1.02;
            letter-spacing: -0.035em;
            word-break: break-word;
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .article-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: clamp(1.4rem, 4.2vw, 2.75rem);
            line-height: 1.18;
            letter-spacing: -0.025em;
            word-break: break-word;
            overflow-wrap: break-word;
            hyphens: auto;
        }

        .hero-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: clamp(1.45rem, 4.5vw, 2.85rem);
            line-height: 1.18;
            letter-spacing: -0.025em;
            word-break: break-word;
            overflow-wrap: break-word;
            hyphens: auto;
        }

        .article-subtitle {
            font-size: clamp(1.05rem, 2.6vw, 1.25rem);
            line-height: 1.45;
        }

        .drop-cap-fluid:first-letter {
            float: left;
            font-size: clamp(3.2rem, 8vw, 4.2rem);
            line-height: 0.85;
            padding-right: 0.5rem;
            padding-top: 0.15rem;
            font-weight: 800;
            color: #121212;
        }

        /* Micro-interação: Links com Sublinhado Animado Neo-Clássico */
        .neo-link {
            position: relative;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        .neo-link::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 1.5px;
            bottom: -2px;
            left: 0;
            background-color: var(--editorial-red);
            transform: scaleX(0);
            transform-origin: bottom right;
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .neo-link:hover::after {
            transform: scaleX(1);
            transform-origin: bottom left;
        }

        /* Efeitos de Transição de Rolagem (Fade-in e Slide-up) */
        .reveal-on-scroll {
            opacity: 0;
            transform: translateY(18px);
            transition: opacity 0.65s cubic-bezier(0.16, 1, 0.3, 1), transform 0.65s cubic-bezier(0.16, 1, 0.3, 1);
            will-change: opacity, transform;
        }
        .reveal-on-scroll.in-view {
            opacity: 1;
            transform: translateY(0);
        }

        /* Cabeçalho Retrátil Sticky NYT */
        #site-header {
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }
        #site-header.is-scrolled {
            background-color: rgba(244, 241, 234, 0.96);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            box-shadow: 0 4px 14px rgba(18, 18, 18, 0.06);
            border-bottom: 1px solid #D1CEC7;
            padding-top: 0.4rem;
            padding-bottom: 0.4rem;
        }
        #site-header.is-scrolled .masthead-title {
            font-size: clamp(1.4rem, 3.8vw, 2.1rem);
        }
        #site-header.is-scrolled .masthead-subline {
            display: none;
        }
        #site-header.is-scrolled .masthead-borders {
            border-top: none;
            border-bottom: 1px solid #121212;
            padding-bottom: 0.2rem;
            padding-top: 0.2rem;
        }
    </style>
"""

COMMON_SCRIPTS = """
    <script>
        // Micro-interações de rolagem suave (Intersection Observer)
        document.addEventListener('DOMContentLoaded', () => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('in-view');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.08,
                rootMargin: '0px 0px -30px 0px'
            });

            document.querySelectorAll('.reveal-on-scroll').forEach(el => {
                observer.observe(el);
            });

            // Cabeçalho Retrátil (Sticky Shrink Header)
            const header = document.getElementById('site-header');
            if (header) {
                window.addEventListener('scroll', () => {
                    const currentScroll = window.scrollY;
                    if (currentScroll > 45) {
                        header.classList.add('is-scrolled');
                    } else {
                        header.classList.remove('is-scrolled');
                    }
                }, { passive: true });
            }
        });
    </script>
"""

def load_articles():
    files = glob.glob(os.path.join(CONTENT_DIR, "*.json"))
    articles = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                data["_mtime"] = os.path.getmtime(f)
                articles.append(data)
        except Exception as e:
            print(f"Erro ao carregar {f}: {e}")
    # Ordena pelo timestamp mais recente (a última notícia é sempre a Manchete Principal)
    articles.sort(key=lambda a: (a.get("timestamp") or a.get("data_iso") or a.get("_mtime", 0)), reverse=True)
    return articles

def render_header(is_article=False):
    back_link = '<a href="../index.html" class="neo-link inline-flex items-center text-xs font-mono uppercase tracking-wider text-[#8B0000] font-bold">&larr; Voltar à Capa</a>' if is_article else '<span class="text-xs font-mono uppercase tracking-wider text-stone-600">Edição Digital Contínua</span>'
    home_link = "../index.html" if is_article else "index.html"
    
    return f"""
    <!-- Top Metadata Bar NYT Style -->
    <div class="border-b border-[#D1CEC7] py-1.5 px-[1.2rem] sm:px-6 text-xs font-mono text-stone-700 flex justify-between items-center max-w-6xl mx-auto">
        <div class="flex items-center space-x-2 sm:space-x-3 overflow-hidden text-ellipsis whitespace-nowrap">
            <span class="font-bold text-[#121212] shrink-0">BRASÍLIA / BRASIL</span>
            <span class="text-[#D1CEC7]">&bull;</span>
            <span class="hidden sm:inline text-stone-600">Previsão: 100% de umidade na cara de pau</span>
            <span class="hidden sm:inline text-[#D1CEC7]">&bull;</span>
            <span class="text-stone-600">Quinta-feira, 15 de Outubro de 2026</span>
        </div>
        <div class="flex items-center space-x-3 shrink-0">
            {back_link}
        </div>
    </div>

    <!-- Newspaper Masthead with Classic NYT Double Line -->
    <div class="sticky top-0 z-40 bg-[#F4F1EA] border-b border-transparent transition-all duration-300" id="site-header">
        <header class="max-w-6xl mx-auto px-[1.2rem] sm:px-6 pt-3 sm:pt-4 pb-2 sm:pb-3 text-center">
            <div class="masthead-borders py-2 sm:py-3 transition-all duration-300">
                <a href="{home_link}" class="inline-block group">
                    <h1 class="masthead-title font-serif font-black tracking-tight text-[#121212] group-hover:text-[#8B0000] transition-colors duration-300">
                        {PORTAL_NAME}
                    </h1>
                </a>
                <div class="masthead-subline border-t border-b border-[#121212]/80 py-1 sm:py-1.5 mt-2 flex flex-col sm:flex-row justify-between items-center text-xs md:text-sm font-serif italic text-stone-800 gap-1 transition-all duration-300">
                    <span class="hidden md:inline font-mono text-xs uppercase font-normal text-stone-600">Ano I &bull; N&ordm; 01</span>
                    <p class="mx-auto font-medium text-[#121212] tracking-wide text-center px-2">{PORTAL_SLOGAN}</p>
                    <span class="hidden md:inline font-mono text-xs uppercase font-normal text-stone-600">Preço: Sua Paciência</span>
                </div>
            </div>
        </header>
    </div>
    """

def render_footer(is_article=False):
    home_link = "../index.html" if is_article else "index.html"
    return f"""
    <footer class="bg-[#121212] text-stone-300 border-t-4 border-[#8B0000] mt-16 sm:mt-24 pt-10 sm:pt-14 pb-12">
        <div class="max-w-6xl mx-auto px-[1.2rem] sm:px-6 grid grid-cols-1 md:grid-cols-3 gap-8 pb-8 border-b border-stone-800">
            <div>
                <a href="{home_link}" class="inline-block group">
                    <h3 class="font-serif text-2xl font-black text-stone-100 group-hover:text-amber-100 tracking-tight transition-colors">{PORTAL_NAME}</h3>
                </a>
                <p class="mt-3 text-stone-400 text-sm leading-relaxed font-sans">
                    Crônica política ácida, deboche com base factual e comédia de costumes do teatro estatal. Se há pompa e incoerência, há matéria-prima.
                </p>
            </div>
            <div>
                <h4 class="font-mono text-xs uppercase tracking-widest text-[#8B0000] font-bold mb-3">Linha Editorial</h4>
                <p class="text-stone-400 text-sm leading-relaxed font-sans">
                    Nenhum político foi poupado durante a redação destas matérias. O alvo é o poder, o carimbo e a liturgia vazia.
                </p>
            </div>
            <div>
                <h4 class="font-mono text-xs uppercase tracking-widest text-[#8B0000] font-bold mb-3">Acompanhe nas Redes</h4>
                <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center space-x-2 text-stone-200 hover:text-white bg-stone-900 hover:bg-stone-800 border border-stone-700 hover:border-stone-500 px-4 py-2.5 rounded text-sm transition-all duration-300">
                    <svg class="w-5 h-5 fill-current text-pink-500" viewBox="0 0 24 24">
                        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                    <span class="font-medium">Siga no Instagram</span>
                    <span class="text-xs text-stone-400 font-mono">({INSTAGRAM_HANDLE})</span>
                </a>
            </div>
        </div>
        <div class="max-w-6xl mx-auto px-[1.2rem] sm:px-6 pt-6 text-center text-xs font-mono text-stone-500">
            &copy; 2026 {PORTAL_NAME}. Nenhum fato foi distorcido &mdash; o absurdo da realidade brasileira já veio pronto de fábrica.
        </div>
    </footer>
    """

def is_valid_image(url):
    """Retorna True apenas se for uma URL de imagem válida e não nula/vazia"""
    if not url:
        return False
    u = str(url).strip()
    if u.lower() in ("none", "null", "", "undefined"):
        return False
    return u.startswith("http://") or u.startswith("https://") or u.startswith("/") or u.startswith("./") or u.startswith("imagens/") or u.startswith("../imagens/")

def resolver_imagem_artigo(art, is_article=False):
    """
    Resolve a imagem da matéria priorizando a caricatura editorial IA no estilo clássico da Revista MAD Brasil.
    Garante o caminho relativo correto para a Home (imagens/...) ou para os Artigos (../imagens/...).
    """
    slug = art.get("slug", "")
    
    # 1. Verifica se existe caricatura local em imagens/{slug}.*
    for ext in (".jpg", ".png", ".jpeg", ".webp"):
        local_rel = f"imagens/{slug}{ext}"
        local_abs = os.path.join(BASE_DIR, local_rel)
        if os.path.exists(local_abs):
            src = f"../{local_rel}" if is_article else local_rel
            legenda = art.get("legenda_imagem") or f"Caricatura editorial satírica: {art.get('titulo')}"
            credito = art.get("credito_imagem") or "Arte: Caricatura Editorial IA / Ilustração Satírica"
            return src, legenda, credito

    # 2. Se imagem_capa estiver definida
    capa = art.get("imagem_capa")
    if is_valid_image(capa):
        c = str(capa).strip()
        if c.startswith("http://") or c.startswith("https://"):
            src = c
        elif is_article and not c.startswith("../") and not c.startswith("/"):
            src = f"../{c}"
        else:
            src = c
        legenda = art.get("legenda_imagem") or f"Caricatura editorial satírica: {art.get('titulo')}"
        credito = art.get("credito_imagem") or "Arte: Caricatura Editorial IA / Ilustração Satírica"
        return src, legenda, credito

    return None, None, None


def render_audio_player(slug, title, audio_src):
    return f"""
    <!-- Reprodutor de Áudio Editorial (Estilo The New York Times "Listen to this article") -->
    <div class="my-6 sm:my-8 bg-[#FAF9F5] border border-[#D1CEC7] border-l-4 border-l-[#8B0000] p-4 sm:p-5 rounded-sm shadow-xs reveal-on-scroll" id="article-audio-box">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
            <div class="flex items-center space-x-3.5">
                <button id="audio-play-btn" type="button" aria-label="Ouvir crônica narrada" class="w-11 h-11 sm:w-12 sm:h-12 rounded-full bg-[#121212] hover:bg-[#8B0000] text-white flex items-center justify-center shrink-0 shadow-sm transition-all duration-300 hover:scale-105 active:scale-95 cursor-pointer">
                    <!-- Play Icon -->
                    <svg id="audio-play-icon" class="w-5 h-5 ml-0.5 fill-current" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                    <!-- Pause Icon -->
                    <svg id="audio-pause-icon" class="w-5 h-5 fill-current hidden" viewBox="0 0 24 24">
                        <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                    </svg>
                </button>
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="font-mono text-xs uppercase tracking-wider font-bold text-[#8B0000]">OUVIR ESTA CRÔNICA</span>
                        <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#EBE7DE] text-stone-700 font-semibold">Voz Neural</span>
                        <span class="w-2 h-2 rounded-full bg-emerald-600 animate-pulse hidden" id="audio-live-dot" title="Reproduzindo"></span>
                    </div>
                    <div class="font-serif italic text-xs text-stone-600 mt-0.5">
                        Narração satírica com voz neural brasileira &bull; Redação IMPRÓBO
                    </div>
                </div>
            </div>

            <div class="flex items-center space-x-2.5 sm:space-x-3 self-end sm:self-center">
                <!-- Velocidade -->
                <button id="audio-speed-btn" type="button" class="font-mono text-xs px-2.5 py-1 bg-white border border-[#D1CEC7] hover:border-[#121212] rounded text-stone-800 font-semibold transition-colors cursor-pointer select-none" title="Velocidade de reprodução">
                    1.0x
                </button>
                <!-- Mute / Unmute -->
                <button id="audio-mute-btn" type="button" class="text-stone-600 hover:text-[#121212] p-1.5 rounded transition-colors cursor-pointer" title="Silenciar / Ativar som">
                    <svg id="audio-vol-icon" class="w-4 h-4 fill-current" viewBox="0 0 24 24">
                        <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                    </svg>
                    <svg id="audio-mute-icon" class="w-4 h-4 fill-current hidden" viewBox="0 0 24 24">
                        <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73 4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                    </svg>
                </button>
                <!-- Tempo -->
                <span id="audio-time" class="font-mono text-xs text-stone-600 min-w-[75px] text-right font-medium">00:00 / --:--</span>
            </div>
        </div>

        <!-- Barra de Progresso Interativa -->
        <div class="relative w-full h-2.5 bg-[#EBE7DE] rounded-full cursor-pointer group" id="audio-progress-container" title="Clique ou arraste para navegar">
            <div id="audio-progress-bar" class="absolute top-0 left-0 h-full bg-[#8B0000] w-0 transition-all duration-75 ease-linear rounded-full pointer-events-none"></div>
            <div id="audio-scrubber-thumb" class="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-[#121212] border-2 border-white rounded-full shadow-sm opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none -ml-1.5" style="left: 0%;"></div>
        </div>

        <!-- Elemento de Áudio Nativo HTML5 -->
        <audio id="article-audio-elem" src="{audio_src}" preload="metadata"></audio>
    </div>
    """

def render_audio_script():
    return """
    <script>
    document.addEventListener('DOMContentLoaded', () => {
        const audio = document.getElementById('article-audio-elem');
        if (!audio) return;

        const playBtn = document.getElementById('audio-play-btn');
        const playIcon = document.getElementById('audio-play-icon');
        const pauseIcon = document.getElementById('audio-pause-icon');
        const liveDot = document.getElementById('audio-live-dot');
        const timeDisplay = document.getElementById('audio-time');
        const progressBar = document.getElementById('audio-progress-bar');
        const progressContainer = document.getElementById('audio-progress-container');
        const thumb = document.getElementById('audio-scrubber-thumb');
        const speedBtn = document.getElementById('audio-speed-btn');
        const muteBtn = document.getElementById('audio-mute-btn');
        const volIcon = document.getElementById('audio-vol-icon');
        const muteIcon = document.getElementById('audio-mute-icon');

        const speeds = [1.0, 1.25, 1.5, 2.0];
        let currentSpeedIdx = 0;

        function formatTime(seconds) {
            if (isNaN(seconds) || seconds < 0) return "--:--";
            const m = Math.floor(seconds / 60);
            const s = Math.floor(seconds % 60);
            return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
        }

        function updateTimeUI() {
            const cur = formatTime(audio.currentTime);
            const dur = formatTime(audio.duration);
            timeDisplay.textContent = `${cur} / ${dur}`;
            if (audio.duration && !isNaN(audio.duration)) {
                const pct = (audio.currentTime / audio.duration) * 100;
                progressBar.style.width = `${pct}%`;
                if (thumb) thumb.style.left = `${pct}%`;
            }
        }

        audio.addEventListener('loadedmetadata', updateTimeUI);
        audio.addEventListener('timeupdate', updateTimeUI);

        // Play / Pause Toggle
        playBtn.addEventListener('click', () => {
            if (audio.paused) {
                audio.play().then(() => {
                    playIcon.classList.add('hidden');
                    pauseIcon.classList.remove('hidden');
                    if (liveDot) liveDot.classList.remove('hidden');
                }).catch(e => {
                    console.error("Erro ao reproduzir áudio:", e);
                });
            } else {
                audio.pause();
                playIcon.classList.remove('hidden');
                pauseIcon.classList.add('hidden');
                if (liveDot) liveDot.classList.add('hidden');
            }
        });

        audio.addEventListener('pause', () => {
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
            if (liveDot) liveDot.classList.add('hidden');
        });

        audio.addEventListener('play', () => {
            playIcon.classList.add('hidden');
            pauseIcon.classList.remove('hidden');
            if (liveDot) liveDot.classList.remove('hidden');
        });

        audio.addEventListener('ended', () => {
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
            if (liveDot) liveDot.classList.add('hidden');
            progressBar.style.width = '0%';
            if (thumb) thumb.style.left = '0%';
            audio.currentTime = 0;
            updateTimeUI();
        });

        // Scrubbing via Click / Drag
        function seek(e) {
            if (!audio.duration || isNaN(audio.duration)) return;
            const rect = progressContainer.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clickX = clientX - rect.left;
            const pct = Math.max(0, Math.min(1, clickX / rect.width));
            audio.currentTime = pct * audio.duration;
            progressBar.style.width = `${pct * 100}%`;
            if (thumb) thumb.style.left = `${pct * 100}%`;
        }

        let isSeeking = false;
        progressContainer.addEventListener('mousedown', (e) => {
            isSeeking = true;
            seek(e);
        });
        window.addEventListener('mousemove', (e) => {
            if (isSeeking) seek(e);
        });
        window.addEventListener('mouseup', () => {
            isSeeking = false;
        });

        // Touch support for mobile
        progressContainer.addEventListener('touchstart', (e) => {
            isSeeking = true;
            seek(e);
        }, { passive: true });
        window.addEventListener('touchmove', (e) => {
            if (isSeeking) seek(e);
        }, { passive: true });
        window.addEventListener('touchend', () => {
            isSeeking = false;
        });

        // Speed Toggle
        speedBtn.addEventListener('click', () => {
            currentSpeedIdx = (currentSpeedIdx + 1) % speeds.length;
            const newSpeed = speeds[currentSpeedIdx];
            audio.playbackRate = newSpeed;
            speedBtn.textContent = `${newSpeed.toFixed(1)}x`;
        });

        // Mute Toggle
        muteBtn.addEventListener('click', () => {
            audio.muted = !audio.muted;
            if (audio.muted) {
                volIcon.classList.add('hidden');
                muteIcon.classList.remove('hidden');
            } else {
                volIcon.classList.remove('hidden');
                muteIcon.classList.add('hidden');
            }
        });
    });
    </script>
    """

def generate_article_page(art):
    slug = art["slug"]
    title = art["titulo"]
    subtitle = art["subtitulo"]
    date_str = art.get("data", "Outubro de 2026")
    category = art.get("categoria", "Crônica Política")
    read_time = art.get("tempo_leitura", "3 min de leitura")
    author = art.get("autor", "Redação Ácida")

    # Reprodutor de Áudio Editorial (Estilo The New York Times)
    audio_file_abs = os.path.join(AUDIO_DIR, f"{slug}.mp3")
    has_audio = os.path.exists(audio_file_abs) or bool(art.get("audio_url"))
    audio_player_html = ""
    audio_script = ""
    if has_audio:
        audio_src = f"../audio/{slug}.mp3"
        audio_player_html = render_audio_player(slug, title, audio_src)
        audio_script = render_audio_script()

    # Caricatura Editorial IA no Estilo Revista MAD Brasil
    img_src, img_legenda, img_credito = resolver_imagem_artigo(art, is_article=True)
    image_html = ""
    if img_src:
        caption_html = ""
        if img_legenda or img_credito:
            legenda_part = f"<span>{img_legenda}</span>" if img_legenda else ""
            credito_part = f"<span class=\"font-sans font-medium text-stone-500 text-[11px] uppercase tracking-wider shrink-0\">{img_credito}</span>" if img_credito else ""
            caption_html = f"""
            <figcaption class="mt-2.5 text-xs sm:text-sm text-stone-600 font-serif italic flex flex-col sm:flex-row justify-between gap-1.5 border-b border-[#D1CEC7]/70 pb-2">
                {legenda_part}
                {credito_part}
            </figcaption>
            """
        image_html = f"""
        <!-- Caricatura Editorial IA / Ilustração Satírica -->
        <figure class="my-6 sm:my-8 reveal-on-scroll">
            <div class="overflow-hidden rounded-sm border border-[#D1CEC7] bg-[#EBE7DE]">
                <img src="{img_src}" alt="{img_legenda or title}" class="w-full h-auto max-h-[560px] object-cover block" loading="lazy">
            </div>
            {caption_html}
        </figure>
        """
    
    # Body paragraphs with fluid responsive drop-cap and reveal animations
    body_html = ""
    for idx, p in enumerate(art.get("corpo", [])):
        if idx == 0:
            body_html += f"""
            <p class="drop-cap-fluid text-lg sm:text-xl text-[#121212] leading-relaxed mb-6 font-serif reveal-on-scroll">
                {p}
            </p>
            """
        else:
            body_html += f"""
            <p class="text-base sm:text-lg text-[#121212]/90 leading-relaxed mb-6 font-serif reveal-on-scroll">
                {p}
            </p>
            """

    # Manual de Emergência / Guia de Sobrevivência do Otário
    guia_raw = art.get("guia_sobrevivencia") or art.get("milagres", [])
    guia_items = ""
    for g in guia_raw:
        g_title = g.get("titulo", "")
        g_text = g.get("texto", "")
        guia_items += f"""
        <li class="pl-2">
            <span class="font-bold text-[#121212] font-serif text-base block mb-1">&bull; {g_title}</span>
            <span class="text-stone-700 text-sm leading-relaxed font-sans">{g_text}</span>
        </li>
        """
        
    guia_html = f"""
    <div class="my-8 sm:my-10 border-2 border-[#121212] bg-[#FAF9F5] p-5 sm:p-7 md:p-8 rounded-sm shadow-sm relative reveal-on-scroll">
        <div class="absolute -top-3 left-4 sm:left-6 bg-[#8B0000] text-white font-mono text-xs uppercase px-2.5 sm:px-3 py-0.5 tracking-widest font-bold">
            MANUAL DE EMERGÊNCIA &bull; GUIA DE SOBREVIVÊNCIA DO OTÁRIO
        </div>
        <h4 class="font-serif font-black text-lg sm:text-xl text-[#121212] mt-1 mb-4">Dicas Práticas Para Não Enlouquecer com a Notícia</h4>
        <ul class="space-y-4">
            {guia_items}
        </ul>
    </div>
    """

    # Contexto Real / Bloco Editorial Clássico (#EBE7DE com borda grossa à esquerda em #121212)
    contexto_real = art.get("contexto_real", "")
    contexto_html = f"""
    <div class="my-8 sm:my-10 border-l-4 border-[#121212] bg-[#EBE7DE] p-5 sm:p-6 rounded-r-sm shadow-sm reveal-on-scroll">
        <div class="flex items-center space-x-2 text-[#121212] font-mono text-xs font-bold uppercase tracking-wider mb-2">
            <svg class="w-4 h-4 text-[#121212] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span>O Contexto Real &bull; Rodapé Factual</span>
        </div>
        <p class="text-[#121212]/95 text-sm leading-relaxed font-sans">
            {contexto_real}
        </p>
    </div>
    """

    page_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {PORTAL_NAME}</title>
    <meta name="description" content="{subtitle}">
    {COMMON_HEAD_STYLES}
</head>
<body class="min-h-screen flex flex-col justify-between selection:bg-[#8B0000] selection:text-white">
    <div>
        {render_header(is_article=True)}

        <!-- NYT Style: Crisp White Article Sheet (#FFFFFF) over Newsprint Cream Canvas (#F4F1EA) -->
        <main class="w-full max-w-4xl mx-auto px-[1.2rem] sm:px-6 my-6 sm:my-10">
            <div class="bg-white border border-[#D1CEC7] shadow-sm rounded-sm p-6 sm:p-10 md:p-14">
                <!-- Article Header -->
                <div class="mb-6 sm:mb-8 border-b border-[#D1CEC7] pb-5 sm:pb-6 reveal-on-scroll">
                    <div class="flex flex-wrap items-center gap-2 mb-3 sm:mb-4 font-mono text-xs">
                        <span class="bg-[#8B0000] text-white font-bold px-2 py-0.5 sm:px-2.5 sm:py-1 tracking-wider uppercase">{category}</span>
                        <span class="text-stone-600">{date_str}</span>
                        <span class="text-[#D1CEC7]">&bull;</span>
                        <span class="text-stone-600">{read_time}</span>
                    </div>

                    <h1 class="article-title font-black text-[#121212] font-serif mb-4">
                        {title}
                    </h1>

                    <p class="article-subtitle text-stone-700 font-serif italic mb-6">
                        {subtitle}
                    </p>

                    <div class="flex items-center justify-between border-t border-[#D1CEC7] pt-3 text-xs font-mono text-stone-600">
                        <div>
                            Texto: <span class="font-bold text-[#121212]">{author}</span>
                        </div>
                        <div>
                            Lente Cínica: <span class="text-[#8B0000] font-bold">100% Calibrada</span>
                        </div>
                    </div>
                </div>

                <!-- Reprodutor de Áudio Editorial (Logo abaixo do cabeçalho) -->
                {audio_player_html}

                <!-- Imagem Principal / Ancoragem Factual (Logo abaixo de Título e Subtítulo) -->
                {image_html}

                <!-- Body -->
                <article class="prose max-w-none">
                    {body_html}
                    {guia_html}
                    {contexto_html}
                </article>

                <!-- Bottom Share / Nav -->
                <div class="mt-10 sm:mt-12 pt-6 border-t border-[#D1CEC7] flex flex-col sm:flex-row gap-4 justify-between items-center reveal-on-scroll">
                    <a href="../index.html" class="neo-link inline-flex items-center text-sm font-mono uppercase tracking-wider text-[#8B0000] font-bold">
                        &larr; Voltar para a Capa
                    </a>
                    <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" class="neo-link text-xs font-mono text-stone-600 hover:text-[#121212] flex items-center space-x-1">
                        <span>Comente no Instagram</span>
                        <span>&rarr;</span>
                    </a>
                </div>
            </div>
        </main>
    </div>

    {render_footer(is_article=True)}
    {COMMON_SCRIPTS}
    {audio_script}
</body>
</html>
"""
    return page_html

def generate_home_page(articles):
    if not articles:
        hero_html = "<div class='py-12 text-center text-stone-500 font-serif'>Nenhuma crônica cadastrada no momento.</div>"
        grid_html = ""
    else:
        hero = articles[0]
        hero_slug = hero["slug"]
        hero_title = hero["titulo"]
        hero_subtitle = hero["subtitulo"]
        hero_date = hero.get("data", "Outubro de 2026")
        hero_snippet = hero.get("corpo", [""])[0] if hero.get("corpo") else ""
        hero_img_src, hero_legenda, hero_credito = resolver_imagem_artigo(hero, is_article=False)

        hero_audio_file = os.path.join(AUDIO_DIR, f"{hero_slug}.mp3")
        hero_has_audio = os.path.exists(hero_audio_file) or bool(hero.get("audio_url"))
        hero_audio_badge = ""
        if hero_has_audio:
            hero_audio_badge = f"""
            <a href="artigos/{hero_slug}.html#article-audio-box" class="inline-flex items-center space-x-1.5 text-xs font-mono text-stone-700 hover:text-[#8B0000] bg-[#EBE7DE] hover:bg-[#D1CEC7] px-2.5 py-0.5 rounded transition-colors" title="Ouvir crônica narrada">
                <svg class="w-3.5 h-3.5 fill-current text-[#8B0000]" viewBox="0 0 24 24">
                    <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                </svg>
                <span class="font-bold">Ouvir Crônica</span>
            </a>
            """

        hero_img_html = ""
        if hero_img_src:
            caption_tag = ""
            if hero_legenda or hero_credito:
                leg_p = f"<span>{hero_legenda}</span>" if hero_legenda else ""
                cred_p = f"<span class=\"font-sans text-[10px] text-stone-500 uppercase font-medium shrink-0\">{hero_credito}</span>" if hero_credito else ""
                caption_tag = f"""
                <div class="px-3 py-1.5 text-xs text-stone-600 font-serif italic border-t border-[#D1CEC7]/70 flex flex-col sm:flex-row justify-between gap-1">
                    {leg_p}
                    {cred_p}
                </div>
                """
            hero_img_html = f"""
            <div class="my-4 sm:my-5 overflow-hidden rounded-sm border border-[#D1CEC7] bg-[#EBE7DE]">
                <a href="artigos/{hero_slug}.html" class="block group/img overflow-hidden">
                    <img src="{hero_img_src}" alt="{hero_legenda or hero_title}" class="w-full h-auto max-h-[460px] object-cover group-hover/img:scale-[1.01] transition-transform duration-300 block" loading="lazy">
                </a>
                {caption_tag}
            </div>
            """

        hero_html = f"""
        <!-- Hero: Manchete Principal NYT Style White Container -->
        <section class="bg-white border border-[#D1CEC7] shadow-sm rounded-sm p-6 sm:p-8 md:p-10 mb-8 sm:mb-12 reveal-on-scroll">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-10 items-start">
                <div class="lg:col-span-8">
                    <div class="flex flex-wrap items-center gap-2 mb-3">
                        <span class="bg-[#8B0000] text-white text-xs font-mono font-bold uppercase tracking-wider px-2 py-0.5">MANCHETE PRINCIPAL</span>
                        <span class="text-xs font-mono text-stone-600">{hero_date}</span>
                        {hero_audio_badge}
                    </div>
                    <a href="artigos/{hero_slug}.html" class="group block">
                        <h2 class="hero-title font-black font-serif text-[#121212] group-hover:text-[#8B0000] transition-colors duration-300 mb-3 sm:mb-4">
                            {hero_title}
                        </h2>
                    </a>
                    <p class="article-subtitle font-serif italic text-stone-700 mb-4 sm:mb-5">
                        {hero_subtitle}
                    </p>
                    {hero_img_html}
                    <p class="text-[#121212]/85 font-serif text-base leading-relaxed line-clamp-3 mb-5 sm:mb-6">
                        {hero_snippet}
                    </p>
                    <a href="artigos/{hero_slug}.html" class="neo-link inline-flex items-center space-x-2 font-mono text-xs uppercase tracking-widest font-bold text-[#8B0000]">
                        <span>Ler crônica completa</span>
                        <span>&rarr;</span>
                    </a>
                </div>

                <!-- Editorial Aside Card (#EBE7DE com borda clássica) -->
                <div class="lg:col-span-4 bg-[#EBE7DE] p-5 sm:p-6 border-l-4 border-[#121212] font-serif rounded-r-sm shadow-sm">
                    <div class="font-mono text-xs uppercase tracking-widest text-[#121212] font-bold mb-2">Frase do Dia na Redação</div>
                    <blockquote class="italic text-[#121212] text-sm md:text-base border-l-2 border-[#8B0000] pl-3 my-2 sm:my-3">
                        &ldquo;A pressa é inimiga da perfeição, mas é mãe adotiva da folga eleitoral de segundo turno.&rdquo;
                    </blockquote>
                    <p class="text-xs font-mono text-stone-600 mt-3 sm:mt-4">&mdash; Provérbio de Botequim Parlamentar</p>
                    <div class="mt-5 pt-3 border-t border-[#D1CEC7]">
                        <span class="text-xs font-mono uppercase font-bold text-[#121212] block mb-1">Aviso ao Leitor</span>
                        <p class="text-xs text-stone-700 leading-relaxed font-sans">
                            Se você sentir raiva lendo os fatos, respire fundo. A culpa não é do redator; é do cartório eleitoral que registrou as candidaturas.
                        </p>
                    </div>
                </div>
            </div>
        </section>
        """

        # Other articles grid
        other_articles = articles[1:]
        if other_articles:
            cards = ""
            for art in other_articles:
                a_slug = art["slug"]
                a_title = art["titulo"]
                a_sub = art.get("subtitulo", "")
                a_date = art.get("data", "")
                a_cat = art.get("categoria", "Crônica")
                card_img_src, card_legenda, card_credito = resolver_imagem_artigo(art, is_article=False)
                
                card_audio_file = os.path.join(AUDIO_DIR, f"{a_slug}.mp3")
                card_has_audio = os.path.exists(card_audio_file) or bool(art.get("audio_url"))
                card_audio_badge = ""
                if card_has_audio:
                    card_audio_badge = f"""
                    <span class="text-[#D1CEC7]">&bull;</span>
                    <a href="artigos/{a_slug}.html#article-audio-box" class="inline-flex items-center space-x-1 text-[11px] font-mono text-stone-700 hover:text-[#8B0000] bg-[#EBE7DE] hover:bg-[#D1CEC7] px-1.5 py-0.5 rounded transition-colors" title="Ouvir versão narrada">
                        <svg class="w-3 h-3 fill-current text-[#8B0000]" viewBox="0 0 24 24">
                            <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                        </svg>
                        <span>Áudio</span>
                    </a>
                    """

                img_card_html = ""
                if card_img_src:
                    img_card_html = f"""
                    <div class="mb-3 overflow-hidden rounded-sm border border-[#D1CEC7] bg-[#EBE7DE]">
                        <img src="{card_img_src}" alt="{a_title}" class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300 block" loading="lazy">
                    </div>
                    """
                cards += f"""
                <article class="reveal-on-scroll border border-[#D1CEC7] p-5 bg-white hover:shadow-md transition-all duration-300 flex flex-col justify-between rounded-sm">
                    <div>
                        {img_card_html}
                        <div class="flex flex-wrap items-center gap-2 text-xs font-mono mb-2">
                            <span class="text-[#8B0000] font-bold uppercase">{a_cat}</span>
                            <span class="text-[#D1CEC7]">&bull;</span>
                            <span class="text-stone-600">{a_date}</span>
                            {card_audio_badge}
                        </div>
                        <a href="artigos/{a_slug}.html" class="block group">
                            <h3 class="font-serif font-bold text-lg sm:text-xl text-[#121212] group-hover:text-[#8B0000] transition-colors duration-300 leading-snug mb-2">
                                {a_title}
                            </h3>
                        </a>
                        <p class="font-serif italic text-sm text-stone-600 line-clamp-3 mb-4">
                            {a_sub}
                        </p>
                    </div>
                    <a href="artigos/{a_slug}.html" class="neo-link font-mono text-xs uppercase font-bold text-[#8B0000] inline-flex items-center space-x-1">
                        <span>Ler mais</span>
                        <span>&rarr;</span>
                    </a>
                </article>
                """
            grid_html = f"""
            <section class="reveal-on-scroll">
                <div class="border-b border-[#121212] pb-2 mb-6 flex items-center justify-between">
                    <h2 class="font-serif text-xl sm:text-2xl font-black text-[#121212] tracking-tight">ARQUIVO DA INFÂMIA &bull; OUTRAS CRÔNICAS</h2>
                    <span class="font-mono text-xs text-stone-600 uppercase">{len(other_articles)} crônica(s)</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {cards}
                </div>
            </section>
            """
        else:
            grid_html = f"""
            <section class="py-6 sm:py-8 text-center border-t border-[#D1CEC7] reveal-on-scroll">
                <span class="font-mono text-xs uppercase tracking-widest text-stone-600">Mais escândalos e gafes em apuração na gráfica...</span>
            </section>
            """

    page_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{PORTAL_NAME} | {PORTAL_SLOGAN}</title>
    <meta name="description" content="Crônicas políticas ácidas, sátira mordaz e jornalismo cético sobre a realidade brasileira.">
    {COMMON_HEAD_STYLES}
</head>
<body class="min-h-screen flex flex-col justify-between selection:bg-[#8B0000] selection:text-white">
    <div>
        {render_header(is_article=False)}

        <!-- Main Content with NYT Style spacing -->
        <main class="max-w-6xl mx-auto px-[1.2rem] sm:px-6 py-6 sm:py-8">
            {hero_html}
            {grid_html}
        </main>
    </div>

    {render_footer(is_article=False)}
    {COMMON_SCRIPTS}
</body>
</html>
"""
    return page_html

def create_vercel_config():
    config = {
        "cleanUrls": True,
        "trailingSlash": False,
        "headers": [
            {
                "source": "/(.*)",
                "headers": [
                    {
                        "key": "X-Content-Type-Options",
                        "value": "nosniff"
                    },
                    {
                        "key": "X-Frame-Options",
                        "value": "DENY"
                    },
                    {
                        "key": "X-XSS-Protection",
                        "value": "1; mode=block"
                    }
                ]
            }
        ]
    }
    with open(VERCEL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"Gerado: {VERCEL_JSON_PATH}")

def build_all():
    os.makedirs(ARTIGOS_DIR, exist_ok=True)
    articles = load_articles()
    print(f"Encontrados {len(articles)} artigos em {CONTENT_DIR}")

    # Generate individual article HTMLs
    for art in articles:
        slug = art["slug"]
        out_path = os.path.join(ARTIGOS_DIR, f"{slug}.html")
        html = generate_article_page(art)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Artigo gerado: {out_path}")

    # Generate index.html
    home_html = generate_home_page(articles)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(home_html)
    print(f"Home gerada: {INDEX_PATH}")

    # Generate vercel.json
    create_vercel_config()
    print("Build NYT Papel Creme finalizado com sucesso!")

if __name__ == "__main__":
    build_all()
