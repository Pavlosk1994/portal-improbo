#!/usr/bin/env python3
"""
Gerador de Site Estático - O ÍMPROBO (Design Neo-Clássico)
Une a nobreza de um jornal clássico à fluidez de uma aplicação web moderna de alto padrão.
100% estático, compatível com Vercel, ultra-rápido e responsivo.
"""

import os
import json
import glob
from datetime import datetime

PORTAL_NAME = "O ÍMPROBO"
PORTAL_SLOGAN = "A crônica semanal da falta de decoro e do absurdo nacional."
INSTAGRAM_URL = "https://instagram.com"
INSTAGRAM_HANDLE = "@oimprobo"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
ARTIGOS_DIR = os.path.join(BASE_DIR, "artigos")
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
VERCEL_JSON_PATH = os.path.join(BASE_DIR, "vercel.json")

COMMON_HEAD_STYLES = """
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,800;1,6..72,400;1,6..72,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-ivory: #F9F8F3;
            --text-charcoal: #111111;
            --editorial-red: #8B0000;
        }

        body {
            background-color: var(--bg-ivory);
            color: var(--text-charcoal);
            font-family: 'Newsreader', Georgia, serif;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
        }

        .font-sans {
            font-family: 'Inter', system-ui, sans-serif;
        }

        /* Tipografia Fluida Responsiva com clamp() */
        .masthead-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: clamp(2.2rem, 7.5vw, 4.6rem);
            line-height: 1.05;
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
            color: #111111;
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
            transform: translateY(20px);
            transition: opacity 0.65s cubic-bezier(0.16, 1, 0.3, 1), transform 0.65s cubic-bezier(0.16, 1, 0.3, 1);
            will-change: opacity, transform;
        }
        .reveal-on-scroll.in-view {
            opacity: 1;
            transform: translateY(0);
        }

        /* Cabeçalho Retrátil Sticky Suave */
        #site-header {
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }
        #site-header.is-scrolled {
            background-color: rgba(249, 248, 243, 0.95);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            box-shadow: 0 4px 12px rgba(17, 17, 17, 0.05);
            border-bottom-color: rgba(17, 17, 17, 0.15);
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }
        #site-header.is-scrolled .masthead-title {
            font-size: clamp(1.5rem, 4vw, 2.2rem);
        }
        #site-header.is-scrolled .masthead-subline {
            display: none;
        }
        #site-header.is-scrolled .masthead-border {
            border-bottom-width: 1px;
            padding-bottom: 0.25rem;
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
                let lastScroll = 0;
                window.addEventListener('scroll', () => {
                    const currentScroll = window.scrollY;
                    if (currentScroll > 50) {
                        header.classList.add('is-scrolled');
                    } else {
                        header.classList.remove('is-scrolled');
                    }
                    lastScroll = currentScroll;
                }, { passive: true });
            }
        });
    </script>
"""

def load_articles():
    files = glob.glob(os.path.join(CONTENT_DIR, "*.json"))
    articles = []
    for f in sorted(files, reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                articles.append(data)
        except Exception as e:
            print(f"Erro ao carregar {f}: {e}")
    return articles

def render_header(is_article=False):
    back_link = '<a href="../index.html" class="neo-link inline-flex items-center text-xs font-mono uppercase tracking-wider text-[#8B0000] font-bold">&larr; Voltar à Capa</a>' if is_article else '<span class="text-xs font-mono uppercase tracking-wider text-stone-500">Edição Digital Contínua</span>'
    home_link = "../index.html" if is_article else "index.html"
    
    return f"""
    <!-- Top Metadata Bar -->
    <div class="border-b border-[#111111]/15 py-1.5 px-[1.2rem] sm:px-6 text-xs font-mono text-stone-600 flex justify-between items-center max-w-6xl mx-auto">
        <div class="flex items-center space-x-2 sm:space-x-3 overflow-hidden text-ellipsis whitespace-nowrap">
            <span class="font-bold text-[#111111] shrink-0">BRASÍLIA / BRASIL</span>
            <span class="hidden sm:inline">&bull;</span>
            <span class="hidden sm:inline text-stone-500">Previsão: 100% de umidade na cara de pau</span>
        </div>
        <div class="flex items-center space-x-3 shrink-0">
            {back_link}
        </div>
    </div>

    <!-- Newspaper Masthead with Retractable Sticky Header -->
    <div class="sticky top-0 z-40 bg-[#F9F8F3] border-b border-transparent transition-all duration-300" id="site-header">
        <header class="max-w-6xl mx-auto px-[1.2rem] sm:px-6 pt-3 sm:pt-5 pb-3 text-center">
            <div class="masthead-border border-b-2 sm:border-b-4 border-[#111111] pb-2 sm:pb-3 transition-all duration-300">
                <a href="{home_link}" class="inline-block group">
                    <h1 class="masthead-title font-serif font-black tracking-tight text-[#111111] group-hover:text-[#8B0000] transition-colors duration-300">
                        {PORTAL_NAME}
                    </h1>
                </a>
                <div class="masthead-subline border-t border-b border-[#111111]/80 py-1 sm:py-1.5 mt-2 sm:mt-3 flex flex-col sm:flex-row justify-between items-center text-xs md:text-sm font-serif italic text-stone-800 gap-1 transition-all duration-300">
                    <span class="hidden md:inline font-mono text-xs uppercase font-normal text-stone-500">Ano I &bull; N&ordm; 01</span>
                    <p class="mx-auto font-medium text-[#111111] tracking-wide text-center px-2">{PORTAL_SLOGAN}</p>
                    <span class="hidden md:inline font-mono text-xs uppercase font-normal text-stone-500">Preço: Sua Paciência</span>
                </div>
            </div>
        </header>
    </div>
    """

def render_footer(is_article=False):
    home_link = "../index.html" if is_article else "index.html"
    return f"""
    <footer class="bg-[#111111] text-stone-300 border-t-4 border-[#8B0000] mt-16 sm:mt-24 pt-10 sm:pt-14 pb-12">
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

def generate_article_page(art):
    slug = art["slug"]
    title = art["titulo"]
    subtitle = art["subtitulo"]
    date_str = art.get("data", "Outubro de 2026")
    category = art.get("categoria", "Crônica Política")
    read_time = art.get("tempo_leitura", "3 min de leitura")
    author = art.get("autor", "Redação Ácida")
    
    # Body paragraphs with fluid responsive drop-cap and reveal animations
    body_html = ""
    for idx, p in enumerate(art.get("corpo", [])):
        if idx == 0:
            body_html += f"""
            <p class="drop-cap-fluid text-lg sm:text-xl text-[#111111] leading-relaxed mb-6 font-serif reveal-on-scroll">
                {p}
            </p>
            """
        else:
            body_html += f"""
            <p class="text-base sm:text-lg text-[#111111]/90 leading-relaxed mb-6 font-serif reveal-on-scroll">
                {p}
            </p>
            """

    # Milagres / Pontos-chave
    milagres_items = ""
    for m in art.get("milagres", []):
        m_title = m.get("titulo", "")
        m_text = m.get("texto", "")
        milagres_items += f"""
        <li class="pl-2">
            <span class="font-bold text-[#111111] font-serif text-base block mb-1">&bull; {m_title}</span>
            <span class="text-stone-700 text-sm leading-relaxed font-sans">{m_text}</span>
        </li>
        """
        
    milagres_html = f"""
    <div class="my-8 sm:my-10 border-2 border-[#111111] bg-[#FAF9F5] p-5 sm:p-7 md:p-8 rounded-sm shadow-sm relative reveal-on-scroll">
        <div class="absolute -top-3 left-4 sm:left-6 bg-[#8B0000] text-white font-mono text-xs uppercase px-2.5 sm:px-3 py-0.5 tracking-widest font-bold">
            OS MILAGRES &bull; PONTOS-CHAVE
        </div>
        <h4 class="font-serif font-black text-lg sm:text-xl text-[#111111] mt-1 mb-4">O Balanço Sarcástico da Medida</h4>
        <ul class="space-y-4">
            {milagres_items}
        </ul>
    </div>
    """

    # Contexto Real
    contexto_real = art.get("contexto_real", "")
    contexto_html = f"""
    <div class="my-8 sm:my-10 border-l-4 border-stone-600 bg-[#F2EFE9] p-4 sm:p-6 rounded-r-sm reveal-on-scroll">
        <div class="flex items-center space-x-2 text-stone-700 font-mono text-xs font-bold uppercase tracking-wider mb-2">
            <svg class="w-4 h-4 text-stone-700 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span>O Contexto Real &bull; Rodapé Factual</span>
        </div>
        <p class="text-[#111111]/90 text-sm leading-relaxed font-sans">
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

        <!-- Article Container with Neo-Clássico padding and breathing room -->
        <main class="w-full max-w-3xl mx-auto px-[1.2rem] sm:px-6 md:px-8 py-6 sm:py-10">
            <!-- Article Header -->
            <div class="mb-6 sm:mb-8 border-b border-[#111111]/20 pb-5 sm:pb-6 reveal-on-scroll">
                <div class="flex flex-wrap items-center gap-2 mb-3 sm:mb-4 font-mono text-xs">
                    <span class="bg-[#8B0000] text-white font-bold px-2 py-0.5 sm:px-2.5 sm:py-1 tracking-wider uppercase">{category}</span>
                    <span class="text-stone-600">{date_str}</span>
                    <span class="text-stone-400">&bull;</span>
                    <span class="text-stone-600">{read_time}</span>
                </div>

                <h1 class="article-title font-black text-[#111111] font-serif mb-4">
                    {title}
                </h1>

                <p class="article-subtitle text-stone-700 font-serif italic mb-6">
                    {subtitle}
                </p>

                <div class="flex items-center justify-between border-t border-[#111111]/15 pt-3 text-xs font-mono text-stone-600">
                    <div>
                        Texto: <span class="font-bold text-[#111111]">{author}</span>
                    </div>
                    <div>
                        Lente Cínica: <span class="text-[#8B0000] font-bold">100% Calibrada</span>
                    </div>
                </div>
            </div>

            <!-- Body -->
            <article class="prose max-w-none">
                {body_html}
                {milagres_html}
                {contexto_html}
            </article>

            <!-- Bottom Share / Nav -->
            <div class="mt-10 sm:mt-12 pt-6 border-t border-[#111111]/20 flex flex-col sm:flex-row gap-4 justify-between items-center reveal-on-scroll">
                <a href="../index.html" class="neo-link inline-flex items-center text-sm font-mono uppercase tracking-wider text-[#8B0000] font-bold">
                    &larr; Voltar para a Capa
                </a>
                <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" class="neo-link text-xs font-mono text-stone-600 hover:text-[#111111] flex items-center space-x-1">
                    <span>Comente no Instagram</span>
                    <span>&rarr;</span>
                </a>
            </div>
        </main>
    </div>

    {render_footer(is_article=True)}
    {COMMON_SCRIPTS}
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

        hero_html = f"""
        <!-- Hero: Manchete Principal -->
        <section class="mb-10 sm:mb-14 border-b-2 border-[#111111] pb-8 sm:pb-12 reveal-on-scroll">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
                <div class="lg:col-span-8">
                    <div class="flex items-center space-x-2 sm:space-x-3 mb-2 sm:mb-3">
                        <span class="bg-[#8B0000] text-white text-xs font-mono font-bold uppercase tracking-wider px-2 py-0.5">MANCHETE PRINCIPAL</span>
                        <span class="text-xs font-mono text-stone-600">{hero_date}</span>
                    </div>
                    <a href="artigos/{hero_slug}.html" class="group block">
                        <h2 class="hero-title font-black font-serif text-[#111111] group-hover:text-[#8B0000] transition-colors duration-300 mb-3 sm:mb-4">
                            {hero_title}
                        </h2>
                    </a>
                    <p class="article-subtitle font-serif italic text-stone-700 mb-4 sm:mb-5">
                        {hero_subtitle}
                    </p>
                    <p class="text-[#111111]/85 font-serif text-base leading-relaxed line-clamp-3 mb-5 sm:mb-6">
                        {hero_snippet}
                    </p>
                    <a href="artigos/{hero_slug}.html" class="neo-link inline-flex items-center space-x-2 font-mono text-xs uppercase tracking-widest font-bold text-[#8B0000]">
                        <span>Ler crônica completa</span>
                        <span>&rarr;</span>
                    </a>
                </div>

                <!-- Editorial Aside -->
                <div class="lg:col-span-4 bg-[#F2EFE9] p-5 sm:p-6 border-l-2 border-[#111111] font-serif rounded-sm shadow-sm">
                    <div class="font-mono text-xs uppercase tracking-widest text-stone-600 font-bold mb-2">Frase do Dia na Redação</div>
                    <blockquote class="italic text-[#111111] text-sm md:text-base border-l-2 border-[#8B0000] pl-3 my-2 sm:my-3">
                        &ldquo;A pressa é inimiga da perfeição, mas é mãe adotiva da folga eleitoral de segundo turno.&rdquo;
                    </blockquote>
                    <p class="text-xs font-mono text-stone-500 mt-3 sm:mt-4">&mdash; Provérbio de Botequim Parlamentar</p>
                    <div class="mt-5 pt-3 border-t border-[#111111]/15">
                        <span class="text-xs font-mono uppercase font-bold text-[#111111] block mb-1">Aviso ao Leitor</span>
                        <p class="text-xs text-stone-600 leading-relaxed font-sans">
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
                cards += f"""
                <article class="reveal-on-scroll border border-[#111111]/20 p-5 bg-[#FAF9F5] hover:shadow-lg hover:border-[#111111]/40 transition-all duration-300 flex flex-col justify-between rounded-sm">
                    <div>
                        <div class="flex items-center space-x-2 text-xs font-mono mb-2">
                            <span class="text-[#8B0000] font-bold uppercase">{a_cat}</span>
                            <span class="text-stone-400">&bull;</span>
                            <span class="text-stone-600">{a_date}</span>
                        </div>
                        <a href="artigos/{a_slug}.html" class="block group">
                            <h3 class="font-serif font-bold text-lg sm:text-xl text-[#111111] group-hover:text-[#8B0000] transition-colors duration-300 leading-snug mb-2">
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
                <div class="border-b border-[#111111] pb-2 mb-6 flex items-center justify-between">
                    <h2 class="font-serif text-xl sm:text-2xl font-black text-[#111111] tracking-tight">ARQUIVO DA INFÂMIA &bull; OUTRAS CRÔNICAS</h2>
                    <span class="font-mono text-xs text-stone-600 uppercase">{len(other_articles)} crônica(s)</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {cards}
                </div>
            </section>
            """
        else:
            grid_html = f"""
            <section class="py-6 sm:py-8 text-center border-t border-[#111111]/15 reveal-on-scroll">
                <span class="font-mono text-xs uppercase tracking-widest text-stone-500">Mais escândalos e gafes em apuração na gráfica...</span>
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

        <!-- Main Content with responsive Neo-Clássico padding -->
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
    print("Build Neo-Clássico finalizado com sucesso!")

if __name__ == "__main__":
    build_all()
