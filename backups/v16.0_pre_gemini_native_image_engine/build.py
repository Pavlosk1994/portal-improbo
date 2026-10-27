#!/usr/bin/env python3
"""
Gerador de Site Estático - ÍMPROBO (Estética New York Times & Papel Creme)
Fundo papel creme (#F4F1EA), container do artigo em branco puro (#FFFFFF), 
linhas editoriais clássicas com borda dupla (#121212), divisores em #D1CEC7
e caixas factuais em #EBE7DE com borda grossa.
"""

import os
import json
import glob
import html
from datetime import datetime

PORTAL_NAME = "ÍMPROBO"
PORTAL_SLOGAN = "A crônica semanal da falta de decoro e do absurdo nacional."
PORTAL_URL = os.environ.get("PORTAL_URL", "https://improbo.vercel.app").rstrip("/")
INSTAGRAM_URL = "https://instagram.com"
INSTAGRAM_HANDLE = "@improbo"
WHATSAPP_CHANNEL_URL = os.environ.get("WHATSAPP_CHANNEL_URL", "https://whatsapp.com/channel/0029Vb3improbo").rstrip("/")
TELEGRAM_CHANNEL_URL = os.environ.get("TELEGRAM_CHANNEL_URL", "https://t.me/portalimprobo").rstrip("/")

PROVERBIOS_BOTEQUIM = [
    "A pressa é inimiga da perfeição, mas é mãe adotiva da folga eleitoral de segundo turno.",
    "Em terra de emenda parlamentar, quem tem nota fiscal fria é rei do orçamento secreto.",
    "Deus ajuda quem cedo madruga, mas o Centrão fatura alto dormindo até o meio-dia.",
    "Para bom entendedor, meio milhão em dinheiro vivo na cueca basta.",
    "Água mole em pedra dura tanto bate até que vira licitação emergencial sem concorrência.",
    "Quem não tem cão caça com gato; quem não tem voto, arruma cargo vitalício no tribunal.",
    "Diga-me com quem andas no plenário e te direi quanto custou o teu ministério.",
    "Cavalo dado não se olha os dentes, mas fundo partidário se audita com lupa e algema.",
    "A esperança é a última que morre, mas o salário mínimo falece no dia dez de cada mês.",
    "Mais vale um passarinho na mão do que dois ministérios prometidos pelo Planalto.",
    "Quem com ferro fere, com foro privilegiado será salvo pela jurisprudência.",
    "Macaco velho não pula em galho seco sem antes garantir a cota de combustíveis do gabinete.",
    "O pior cego é aquele que não quer ver o reajuste salarial aprovado de madrugada.",
    "Casa de ferreiro, espeto de pau; casa de político, churrasco com verba indenizatória.",
    "Em rio de piranha, jacaré nada de braçada se estiver filiado ao partido do presidente.",
    "Santo de casa não faz milagre, mas marqueteiro de campanha faz até poste virar estadista.",
    "Cada macaco no seu galho, e cada assessor com trinta por cento devolvido na rachadinha.",
    "O seguro morreu de velho, e o deputado se reelegeu prometendo o que nunca vai entregar.",
    "Papagaio come milho, periquito leva a fama e o contribuinte financia o banquete da corte.",
    "Antes só do que mal assessorado por sobrinho em comissão parlamentar fantasma.",
    "Não há bem que sempre dure, nem rombo fiscal que o aumento de tributo não tente cobrir.",
    "Filho feio não tem pai, mas déficit público sempre é culpa do governo anterior.",
    "A caridade começa em casa, preferencialmente na conta bancária do primeiro suplente.",
    "Gato escaldado tem medo de água fria; político investigado tem pânico de operação da PF às 6h.",
    "De grão em grão a galinha enche o papo; de diária em diária o senador compra o iate.",
    "Quem ri por último ri melhor, mas quem votou no vencedor já está chorando no caixa do mercado.",
    "Cão que ladra não morde no plenário, mas abocanha fatias generosas na comissão mista.",
    "Depois da tempestade vem a bonança, e logo depois vem o aumento da alíquota do ICMS.",
    "Devagar se vai ao longe, especialmente na fila de espera do SUS bancada pelo erário.",
    "Onde há fumaça, há fogo; e onde há relator especial, há jabuti embutido na medida provisória.",
    "O combinado não sai caro, mas a conta do banquete oficial sempre sai parcelada pro povo."
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
ARTIGOS_DIR = os.path.join(BASE_DIR, "artigos")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
IMAGENS_DIR = os.path.join(BASE_DIR, "imagens")
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
SOBRE_PATH = os.path.join(BASE_DIR, "sobre.html")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")
ROBOTS_PATH = os.path.join(BASE_DIR, "robots.txt")
VERCEL_JSON_PATH = os.path.join(BASE_DIR, "vercel.json")

COMMON_HEAD_STYLES = r"""
    <meta name="referrer" content="no-referrer">
    <script>
        // Prevenção imediata de flash branco (FOUC)
        (function() {
            try {
                const savedTheme = localStorage.getItem('improbo_theme');
                const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
            } catch (e) {}
        })();
    </script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class'
        }
    </script>
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
            --audio-box-bg: #FAF9F5;
            --text-secondary: #57534e;
        }

        html.dark {
            --bg-nyt: #141416;
            --container-white: #1e1e22;
            --text-charcoal: #f3f3f5;
            --editorial-red: #e03131;
            --border-divider: #333338;
            --box-cream-dark: #26262b;
            --audio-box-bg: #222227;
            --text-secondary: #a1a1aa;
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
            transform: translateY(14px);
            transition: opacity 0.45s ease-out, transform 0.45s ease-out;
            will-change: opacity, transform;
        }
        .reveal-on-scroll.in-view {
            opacity: 1 !important;
            transform: translateY(0) !important;
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

        /* Transição Suave de Tema */
        body {
            transition: background-color 0.25s ease, color 0.25s ease;
        }

        /* Dark Mode Theme Overrides Gerais */
        html.dark .masthead-borders {
            border-top: 1px solid #52525b;
            border-bottom: 3px double #52525b;
        }

        html.dark .masthead-subline {
            border-color: #52525b !important;
            color: #d4d4d8 !important;
        }

        html.dark .editorial-divider {
            border-color: var(--border-divider) !important;
        }

        html.dark .bg-white {
            background-color: var(--container-white) !important;
            border-color: var(--border-divider) !important;
            color: var(--text-charcoal) !important;
        }

        html.dark .bg-\[\#F4F1EA\] {
            background-color: var(--bg-nyt) !important;
        }

        html.dark .bg-\[\#FAF9F5\] {
            background-color: var(--audio-box-bg) !important;
            border-color: var(--border-divider) !important;
        }

        html.dark .bg-\[\#EBE7DE\] {
            background-color: var(--box-cream-dark) !important;
            border-color: var(--border-divider) !important;
            color: var(--text-charcoal) !important;
        }

        html.dark .text-\[\#121212\] {
            color: var(--text-charcoal) !important;
        }

        html.dark .text-\[\#121212\]\/90,
        html.dark .text-\[\#121212\]\/85,
        html.dark .text-\[\#121212\]\/95 {
            color: rgba(243, 243, 245, 0.92) !important;
        }

        html.dark .text-stone-700,
        html.dark .text-stone-600 {
            color: var(--text-secondary) !important;
        }

        html.dark .text-stone-800 {
            color: #e4e4e7 !important;
        }

        html.dark .text-stone-500 {
            color: #71717a !important;
        }

        html.dark .border-\[\#D1CEC7\] {
            border-color: var(--border-divider) !important;
        }

        html.dark .border-\[\#121212\] {
            border-color: #52525b !important;
        }

        html.dark .drop-cap-fluid:first-letter {
            color: var(--text-charcoal) !important;
        }

        html.dark blockquote {
            color: var(--text-charcoal) !important;
        }

        html.dark #article-audio-box {
            background-color: var(--audio-box-bg) !important;
            border-color: var(--border-divider) !important;
        }

        html.dark #audio-progress-container {
            background-color: #2e2e34 !important;
        }

        html.dark #audio-speed-btn {
            background-color: #27272c !important;
            border-color: #3f3f46 !important;
            color: var(--text-charcoal) !important;
        }

        html.dark #audio-play-btn {
            background-color: #f4f4f5 !important;
            color: #141416 !important;
        }

        html.dark #audio-play-btn:hover {
            background-color: var(--editorial-red) !important;
            color: #ffffff !important;
        }

        html.dark #theme-toggle-btn {
            background-color: #26262b !important;
            border-color: #3f3f46 !important;
            color: #f4f4f5 !important;
        }

        html.dark #theme-toggle-btn:hover {
            border-color: #71717a !important;
            background-color: #323238 !important;
        }

        html.dark #site-header.is-scrolled {
            background-color: rgba(20, 20, 22, 0.96) !important;
            border-bottom: 1px solid var(--border-divider) !important;
        }

        html.dark #site-header.is-scrolled .masthead-borders {
            border-bottom: 1px solid #52525b !important;
        }

        /* Dark Mode Overrides para os Novos Recursos */
        html.dark #share-box {
            background-color: var(--box-cream-dark) !important;
            border-color: var(--border-divider) !important;
            border-left-color: #25D366 !important;
        }

        html.dark #btn-copy-link {
            background-color: #27272c !important;
            border-color: #3f3f46 !important;
            color: #f3f3f5 !important;
        }

        html.dark #btn-copy-link:hover {
            border-color: #71717a !important;
            background-color: #323238 !important;
        }

        html.dark #sticky-audio-bar {
            background-color: #1a1a1e !important;
            border-top-color: var(--editorial-red) !important;
            box-shadow: 0 -4px 22px rgba(0, 0, 0, 0.5) !important;
        }

        html.dark #sticky-play-btn {
            background-color: #f4f4f5 !important;
            color: #141416 !important;
        }

        html.dark #sticky-play-btn:hover {
            background-color: var(--editorial-red) !important;
            color: #ffffff !important;
        }

        html.dark #sticky-progress-container {
            background-color: #2e2e34 !important;
        }

        html.dark #termometro-box {
            background-color: var(--box-cream-dark) !important;
            border-color: #52525b !important;
        }

        html.dark .termometro-opcao-btn {
            background-color: #222227 !important;
            border-color: #3f3f46 !important;
            color: #f3f3f5 !important;
        }

        html.dark .termometro-opcao-btn:hover {
            border-color: #71717a !important;
            background-color: #2c2c33 !important;
        }

        html.dark .termometro-opcao-voted {
            background-color: #222227 !important;
            border-color: #3f3f46 !important;
        }

        html.dark #desculpa-box {
            background-color: #1e1e22 !important;
            border-color: #3f3f46 !important;
        }

        html.dark #btn-nova-desculpa {
            background-color: #f4f4f5 !important;
            color: #141416 !important;
        }

        html.dark #btn-nova-desculpa:hover {
            background-color: var(--editorial-red) !important;
            color: #ffffff !important;
        }

        html.dark .filtro-btn:not(.active) {
            background-color: #26262b !important;
            border: 1px solid #3f3f46 !important;
            color: #d4d4d8 !important;
        }

        html.dark .filtro-btn:not(.active):hover {
            background-color: #323238 !important;
            color: #ffffff !important;
        }

        /* Dark Mode Overrides para Newsletter & Canais de Transmissão */
        html.dark #newsletter-box {
            background-color: var(--container-white) !important;
            border-color: var(--border-divider) !important;
        }

        html.dark #newsletter-email-home,
        html.dark #newsletter-email-art,
        html.dark #newsletter-email-sobre {
            background-color: #26262b !important;
            border-color: #3f3f46 !important;
            color: #f3f3f5 !important;
        }

        html.dark #newsletter-email-home::placeholder,
        html.dark #newsletter-email-art::placeholder,
        html.dark #newsletter-email-sobre::placeholder {
            color: #71717a !important;
        }

        /* Dark Mode Overrides para Author Bio (Pavi) */
        html.dark .author-bio-card-sobre {
            background-color: var(--container-white) !important;
            border-color: var(--border-divider) !important;
        }

        html.dark .author-bio-card-sobre h3 {
            color: var(--text-charcoal) !important;
        }

        html.dark .author-bio-card-sobre p {
            color: var(--text-secondary) !important;
        }
    </style>
"""

COMMON_SCRIPTS = """
    <script>
        // Micro-interações de rolagem suave (Intersection Observer)
        document.addEventListener('DOMContentLoaded', () => {
            // Atualização Dinâmica da Data de Hoje no Topo
            const headerDateEl = document.getElementById('live-header-date');
            if (headerDateEl) {
                try {
                    const agora = new Date();
                    const formatador = new Intl.DateTimeFormat('pt-BR', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric'
                    });
                    const partes = formatador.format(agora);
                    headerDateEl.textContent = partes.charAt(0).toUpperCase() + partes.slice(1);
                } catch (e) {}
            }

            // Atualização Diária da Frase do Dia (Provérbios de Botequim Parlamentar)
            const fraseDiaEl = document.getElementById('frase-do-dia-texto');
            if (fraseDiaEl) {
                const proverbiosBotequim = [
                    "A pressa é inimiga da perfeição, mas é mãe adotiva da folga eleitoral de segundo turno.",
                    "Em terra de emenda parlamentar, quem tem nota fiscal fria é rei do orçamento secreto.",
                    "Deus ajuda quem cedo madruga, mas o Centrão fatura alto dormindo até o meio-dia.",
                    "Para bom entendedor, meio milhão em dinheiro vivo na cueca basta.",
                    "Água mole em pedra dura tanto bate até que vira licitação emergencial sem concorrência.",
                    "Quem não tem cão caça com gato; quem não tem voto, arruma cargo vitalício no tribunal.",
                    "Diga-me com quem andas no plenário e te direi quanto custou o teu ministério.",
                    "Cavalo dado não se olha os dentes, mas fundo partidário se audita com lupa e algema.",
                    "A esperança é a última que morre, mas o salário mínimo falece no dia dez de cada mês.",
                    "Mais vale um passarinho na mão do que dois ministérios prometidos pelo Planalto.",
                    "Quem com ferro fere, com foro privilegiado será salvo pela jurisprudência.",
                    "Macaco velho não pula em galho seco sem antes garantir a cota de combustíveis do gabinete.",
                    "O pior cego é aquele que não quer ver o reajuste salarial aprovado de madrugada.",
                    "Casa de ferreiro, espeto de pau; casa de político, churrasco com verba indenizatória.",
                    "Em rio de piranha, jacaré nada de braçada se estiver filiado ao partido do presidente.",
                    "Santo de casa não faz milagre, mas marqueteiro de campanha faz até poste virar estadista.",
                    "Cada macaco no seu galho, e cada assessor com trinta por cento devolvido na rachadinha.",
                    "O seguro morreu de velho, e o deputado se reelegeu prometendo o que nunca vai entregar.",
                    "Papagaio come milho, periquito leva a fama e o contribuinte financia o banquete da corte.",
                    "Antes só do que mal assessorado por sobrinho em comissão parlamentar fantasma.",
                    "Não há bem que sempre dure, nem rombo fiscal que o aumento de tributo não tente cobrir.",
                    "Filho feio não tem pai, mas déficit público sempre é culpa do governo anterior.",
                    "A caridade começa em casa, preferencialmente na conta bancária do primeiro suplente.",
                    "Gato escaldado tem medo de água fria; político investigado tem pânico de operação da PF às 6h.",
                    "De grão em grão a galinha enche o papo; de diária em diária o senador compra o iate.",
                    "Quem ri por último ri melhor, mas quem votou no vencedor já está chorando no caixa do mercado.",
                    "Cão que ladra não morde no plenário, mas abocanha fatias generosas na comissão mista.",
                    "Depois da tempestade vem a bonança, e logo depois vem o aumento da alíquota do ICMS.",
                    "Devagar se vai ao longe, especialmente na fila de espera do SUS bancada pelo erário.",
                    "Onde há fumaça, há fogo; e onde há relator especial, há jabuti embutido na medida provisória.",
                    "O combinado não sai caro, mas a conta do banquete oficial sempre sai parcelada pro povo."
                ];
                const diaAtual = new Date().getDate();
                const proverbioHoje = proverbiosBotequim[(diaAtual - 1) % proverbiosBotequim.length];
                fraseDiaEl.innerHTML = `&ldquo;${proverbioHoje}&rdquo;`;
            }

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('in-view');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0,
                rootMargin: '120px 0px 80px 0px'
            });

            document.querySelectorAll('.reveal-on-scroll').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.top < window.innerHeight + 150) {
                    el.classList.add('in-view');
                } else {
                    observer.observe(el);
                }
            });

            // Blindagem contra espaços em branco: garante visibilidade de todos os elementos
            setTimeout(() => {
                document.querySelectorAll('.reveal-on-scroll:not(.in-view)').forEach(el => {
                    el.classList.add('in-view');
                });
            }, 1000);

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

            // Alternador de Modo Escuro / Noturno (Dark Theme)
            const toggleBtn = document.getElementById('theme-toggle-btn');
            if (toggleBtn) {
                const moonIcon = document.getElementById('theme-moon-icon');
                const sunIcon = document.getElementById('theme-sun-icon');
                const toggleText = document.getElementById('theme-toggle-text');

                function syncUI(isDark) {
                    if (isDark) {
                        if (moonIcon) moonIcon.classList.add('hidden');
                        if (sunIcon) sunIcon.classList.remove('hidden');
                        if (toggleText) toggleText.textContent = 'Modo Claro';
                        toggleBtn.setAttribute('title', 'Alternar para o modo claro');
                        toggleBtn.setAttribute('aria-label', 'Ativar modo claro');
                    } else {
                        if (moonIcon) moonIcon.classList.remove('hidden');
                        if (sunIcon) sunIcon.classList.add('hidden');
                        if (toggleText) toggleText.textContent = 'Modo Escuro';
                        toggleBtn.setAttribute('title', 'Alternar para o modo escuro');
                        toggleBtn.setAttribute('aria-label', 'Ativar modo escuro');
                    }
                }

                syncUI(document.documentElement.classList.contains('dark'));

                toggleBtn.addEventListener('click', () => {
                    const isCurrentlyDark = document.documentElement.classList.contains('dark');
                    const nextDark = !isCurrentlyDark;
                    
                    if (nextDark) {
                        document.documentElement.classList.add('dark');
                        try { localStorage.setItem('improbo_theme', 'dark'); } catch(e) {}
                    } else {
                        document.documentElement.classList.remove('dark');
                        try { localStorage.setItem('improbo_theme', 'light'); } catch(e) {}
                    }
                    syncUI(nextDark);
                });
            }

            // Gerador de Desculpas Oficiais de Brasília
            const btnDesculpa = document.getElementById('btn-nova-desculpa');
            if (btnDesculpa) {
                const desculpas = [
                    "A declaração foi distorcida por uma inteligência artificial financiada por interesses escusos da oposição.",
                    "Não houve dolo, apenas uma interpretação excessivamente literal da Constituição Federal.",
                    "O dinheiro na mala era estritamente para custear a liturgia do cargo e despesas cívicas do gabinete.",
                    "Trata-se de um erro de digitação de R$ 900 milhões no anexo suplementar da Lei de Diretrizes Orçamentárias.",
                    "Fui hackeado às 3h da manhã por um operador patriota com domicílio fiscal no Paraguai.",
                    "A indicação de parentes para estatais visa unicamente fortalecer os laços fraternos da República.",
                    "A catraca na praia é apenas para aferir a sustentabilidade ecológica da brisa marítima privatizada.",
                    "O diálogo vazado ocorreu em contexto estritamente filosófico e metafórico durante um cafezinho.",
                    "Votei pelo aumento do fundo partidário de R$ 5 bilhões para salvar a democracia do perigo da austeridade.",
                    "A concessionária esclarece que o apagão é um convite poético à reflexão coletiva à luz de velas.",
                    "O apostador do Bolsa Família estava realizando uma operação de hedge cambial de alto risco no Tigrinho.",
                    "O sigilo de 100 anos é uma homenagem preventiva à posteridade histórica dos nossos descendentes.",
                    "O ministro estava no camarim VIP apenas prestando consultoria informal sobre a liturgia das togas.",
                    "Houve um equívoco de redação do estagiário júnior, que já foi transferido para uma embaixada em Paris.",
                    "Tudo foi executado com rigor absoluto dentro das quatro linhas da conveniência orçamentária."
                ];
                let lastIdx = 0;
                const textoEl = document.getElementById('desculpa-texto');
                const spinIcon = document.getElementById('desculpa-spin-icon');
                const protoEl = document.getElementById('desculpa-protocolo');
                let degrees = 0;

                btnDesculpa.addEventListener('click', () => {
                    degrees += 360;
                    if (spinIcon) spinIcon.style.transform = `rotate(${degrees}deg)`;
                    
                    let nextIdx;
                    do {
                        nextIdx = Math.floor(Math.random() * desculpas.length);
                    } while (nextIdx === lastIdx && desculpas.length > 1);
                    lastIdx = nextIdx;

                    if (textoEl) {
                        textoEl.style.opacity = '0';
                        setTimeout(() => {
                            textoEl.innerHTML = `&ldquo;${desculpas[nextIdx]}&rdquo;`;
                            textoEl.style.opacity = '1';
                        }, 180);
                    }

                    if (protoEl) {
                        protoEl.textContent = `Protocolo nº ${Math.floor(1000 + Math.random() * 9000)}/2026 arquivado com sucesso.`;
                    }
                });
            }

            // Filtro Rápido por Alvo da Sátira na Capa
            const filterBtns = document.querySelectorAll('.filtro-btn');
            if (filterBtns.length > 0) {
                const heroSection = document.getElementById('hero-article-section');
                const gridCards = document.querySelectorAll('.article-card-item');
                const contador = document.getElementById('filtro-contador');
                const semResultados = document.getElementById('filtro-sem-resultados');

                filterBtns.forEach(btn => {
                    btn.addEventListener('click', () => {
                        const filter = btn.getAttribute('data-filter');

                        // Atualizar botões
                        filterBtns.forEach(b => {
                            b.classList.remove('active', 'bg-[#8B0000]', 'text-white', 'shadow-xs', 'font-bold');
                            b.classList.add('bg-[#EBE7DE]', 'text-stone-800', 'font-medium');
                        });
                        btn.classList.add('active', 'bg-[#8B0000]', 'text-white', 'shadow-xs', 'font-bold');
                        btn.classList.remove('bg-[#EBE7DE]', 'text-stone-800', 'font-medium');

                        let visibleCount = 0;

                        // Filtrar Manchete Hero
                        if (heroSection) {
                            const heroAlvo = heroSection.getAttribute('data-alvo');
                            if (filter === 'all' || heroAlvo === filter) {
                                heroSection.classList.remove('hidden');
                                visibleCount++;
                            } else {
                                heroSection.classList.add('hidden');
                            }
                        }

                        // Filtrar Cards do Grid
                        gridCards.forEach(card => {
                            const cardAlvo = card.getAttribute('data-alvo');
                            if (filter === 'all' || cardAlvo === filter) {
                                card.classList.remove('hidden');
                                visibleCount++;
                            } else {
                                card.classList.add('hidden');
                            }
                        });

                        // Atualizar contador e mensagem
                        if (contador) {
                            if (filter === 'all') {
                                contador.textContent = `Exibindo todas as ${visibleCount} crônicas`;
                            } else {
                                const btnText = btn.textContent.replace(/\\(\\d+\\)/, '').trim();
                                contador.textContent = `Exibindo ${visibleCount} crônica(s) sobre: ${btnText}`;
                            }
                        }

                        if (semResultados) {
                            if (visibleCount === 0) {
                                semResultados.classList.remove('hidden');
                            } else {
                                semResultados.classList.add('hidden');
                            }
                        }
                    });
                });
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

def obter_data_formatada_pt():
    """Gera a data de hoje formatada em português brasileiro (ex: Quarta-feira, 21 de Outubro de 2026)"""
    agora = datetime.now()
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    meses_ano = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    dia_nome = dias_semana[agora.weekday()]
    mes_nome = meses_ano[agora.month - 1]
    return f"{dia_nome}, {agora.day} de {mes_nome} de {agora.year}"

def render_header(is_article=False):
    back_link = '<a href="../index.html" class="neo-link inline-flex items-center text-xs font-mono uppercase tracking-wider text-[#8B0000] font-bold">&larr; Voltar à Capa</a>' if is_article else '<span class="text-xs font-mono uppercase tracking-wider text-stone-600">Edição Digital Contínua</span>'
    home_link = "../index.html" if is_article else "index.html"
    data_hoje = obter_data_formatada_pt()
    
    return f"""
    <!-- Top Metadata Bar NYT Style -->
    <div class="border-b border-[#D1CEC7] py-1.5 px-[1.2rem] sm:px-6 text-xs font-mono text-stone-700 flex justify-between items-center max-w-6xl mx-auto transition-colors">
        <div class="flex items-center space-x-2 sm:space-x-3 overflow-hidden text-ellipsis whitespace-nowrap">
            <span class="font-bold text-[#121212] shrink-0">BRASÍLIA / BRASIL</span>
            <span class="text-[#D1CEC7]">&bull;</span>
            <span class="hidden sm:inline text-stone-600">Previsão: 100% de umidade na cara de pau</span>
            <span class="hidden sm:inline text-[#D1CEC7]">&bull;</span>
            <span id="live-header-date" class="text-stone-600">{data_hoje}</span>
        </div>
        <div class="flex items-center space-x-2 sm:space-x-3 shrink-0">
            {back_link}
            <span class="text-[#D1CEC7]">&bull;</span>
            <!-- Botão Alternador Modo Escuro (Dark Mode) -->
            <button id="theme-toggle-btn" type="button" aria-label="Alternar modo escuro" title="Alternar entre modo claro e escuro" class="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded text-[11px] sm:text-xs font-mono font-medium transition-all duration-200 border border-[#D1CEC7] hover:border-[#121212] bg-white text-stone-700 hover:text-[#121212] cursor-pointer shadow-2xs">
                <!-- Moon Icon (visível no modo claro) -->
                <svg id="theme-moon-icon" class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                    <path d="M12.3 2a10 10 0 0 0-.19 14 10 10 0 0 0 11.89 4 1 1 0 0 0 .62-1.28 1 1 0 0 0-.91-.72 8 8 0 0 1-7.1-7.1 1 1 0 0 0-.72-.91A1 1 0 0 0 15 10a8.07 8.07 0 0 1-2.7-8 1 1 0 0 0-1.28-.62A1 1 0 0 0 10.3 2z"/>
                </svg>
                <!-- Sun Icon (visível no modo escuro) -->
                <svg id="theme-sun-icon" class="w-3.5 h-3.5 fill-current text-amber-400 hidden" viewBox="0 0 24 24">
                    <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.29 1.29c.39.39 1.02.39 1.41 0 .39-.39.39-1.02 0-1.41L5.99 4.58zm12.37 12.37a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.29 1.29c.39.39 1.02.39 1.41 0 .39-.39.39-1.02 0-1.41l-1.29-1.29zm-13.78 1.41l1.29-1.29c.39-.39.39-1.02 0-1.41a.996.996 0 0 0-1.41 0l-1.29 1.29a.996.996 0 0 0 0 1.41c.39.38 1.03.38 1.41 0zm12.37-12.37l1.29-1.29c.39-.39.39-1.02 0-1.41a.996.996 0 0 0-1.41 0l-1.29 1.29c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0z"/>
                </svg>
                <span id="theme-toggle-text" class="hidden sm:inline">Modo Escuro</span>
            </button>
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
    sobre_link = "../sobre.html" if is_article else "sobre.html"
    sitemap_link = "../sitemap.xml" if is_article else "sitemap.xml"
    sala_link = "../sala-de-maquinas.html" if is_article else "sala-de-maquinas.html"
    autor_img_src = "../imagens/autor.png" if is_article else "imagens/autor.png"
    return f"""
    <footer class="bg-[#121212] text-stone-300 border-t-4 border-[#8B0000] mt-16 sm:mt-24 pt-10 sm:pt-14 pb-12">
        <div class="max-w-6xl mx-auto px-[1.2rem] sm:px-6">
            <!-- Author Bio Card: Pavi -->
            <div class="mb-10 sm:mb-12 p-5 sm:p-7 bg-[#1c1c20] border border-stone-800 rounded-sm shadow-sm flex flex-col sm:flex-row items-center sm:items-start gap-5 sm:gap-6 reveal-on-scroll">
                <div class="relative shrink-0">
                    <img src="{autor_img_src}" alt="Caricatura de Pavi - Diretor Editorial &amp; Fundador" class="w-20 h-20 sm:w-24 sm:h-24 rounded-full object-cover object-center border-2 border-[#8B0000] shadow-md bg-stone-900" loading="lazy">
                    <span class="absolute -bottom-1 -right-1 bg-[#8B0000] text-white text-[9px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded shadow-xs">AUTOR</span>
                </div>
                <div class="flex-1 text-center sm:text-left">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
                        <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2">
                            <h4 class="font-serif font-black text-xl text-stone-100 tracking-tight">Pavi</h4>
                            <span class="text-stone-600 hidden sm:inline">&bull;</span>
                            <span class="font-mono text-xs text-[#8B0000] font-bold uppercase tracking-wider">Diretor Editorial &amp; Fundador</span>
                        </div>
                        <span class="text-[11px] font-mono text-stone-500 uppercase">Brasília / Brasil</span>
                    </div>
                    <p class="font-serif italic text-stone-300 text-sm sm:text-base leading-relaxed max-w-3xl">
                        &ldquo;Entusiasta de jornalismo independente, tecnologia e crônica política. Acredita que a sátira não é apenas diversão, mas o único escudo democrático contra a arrogância de quem manda. Escreve e programa para lembrar aos governantes que o rei está sempre nu.&rdquo;
                    </p>
                </div>
            </div>

            <!-- Colunas do Rodapé -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 pb-8 border-b border-stone-800">
                <div>
                    <a href="{home_link}" class="inline-block group">
                        <h3 class="font-serif text-2xl font-black text-stone-100 group-hover:text-amber-100 tracking-tight transition-colors">{PORTAL_NAME}</h3>
                    </a>
                    <p class="mt-3 text-stone-400 text-sm leading-relaxed font-sans">
                        Crônica política ácida, deboche com base factual e comédia de costumes do teatro estatal. Se há pompa e incoerência, há matéria-prima.
                    </p>
                </div>
                <div>
                    <h4 class="font-mono text-xs uppercase tracking-widest text-[#8B0000] font-bold mb-3">Linha Editorial &amp; Legal</h4>
                    <p class="text-stone-400 text-sm leading-relaxed font-sans mb-3">
                        Nenhum político foi poupado durante a redação destas matérias. O alvo é o poder, o carimbo e a liturgia vazia.
                    </p>
                    <a href="{sobre_link}" class="inline-flex items-center space-x-1.5 text-xs font-mono font-bold uppercase tracking-wider text-amber-200 hover:text-white transition-colors">
                        <span>Aviso Legal &amp; Manifesto</span>
                        <span>&rarr;</span>
                    </a>
                </div>
                <div>
                    <h4 class="font-mono text-xs uppercase tracking-widest text-[#8B0000] font-bold mb-3">Acompanhe nas Redes &amp; Canais</h4>
                    <div class="flex flex-col space-y-2">
                        <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center space-x-2 text-stone-200 hover:text-white bg-stone-900 hover:bg-stone-800 border border-stone-700 hover:border-stone-500 px-3.5 py-2 rounded text-xs transition-all duration-300">
                            <svg class="w-4 h-4 fill-current text-pink-500 shrink-0" viewBox="0 0 24 24">
                                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                            </svg>
                            <span class="font-medium">Instagram ({INSTAGRAM_HANDLE})</span>
                        </a>
                        <a href="{WHATSAPP_CHANNEL_URL}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center space-x-2 text-stone-200 hover:text-white bg-stone-900 hover:bg-stone-800 border border-stone-700 hover:border-stone-500 px-3.5 py-2 rounded text-xs transition-all duration-300">
                            <svg class="w-4 h-4 fill-current text-emerald-400 shrink-0" viewBox="0 0 24 24">
                                <path d="M12 2C6.477 2 2 6.477 2 12c0 1.89.525 3.66 1.438 5.168L2 22l4.99-1.408C8.423 21.493 10.155 22 12 22c5.523 0 10-4.477 10-10S17.523 2 12 2zm0 18.167c-1.69 0-3.26-.525-4.56-1.423l-.327-.225-2.964.836.84-2.888-.242-.344C3.784 14.805 3.25 13.447 3.25 12c0-4.825 3.925-8.75 8.75-8.75s8.75 3.925 8.75 8.75-3.925 8.75-8.75 8.75z"/>
                            </svg>
                            <span class="font-medium">Canal WhatsApp</span>
                        </a>
                        <a href="{TELEGRAM_CHANNEL_URL}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center space-x-2 text-stone-200 hover:text-white bg-stone-900 hover:bg-stone-800 border border-stone-700 hover:border-stone-500 px-3.5 py-2 rounded text-xs transition-all duration-300">
                            <svg class="w-4 h-4 fill-current text-sky-400 shrink-0" viewBox="0 0 24 24">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.19-.08-.05-.19-.02-.27 0-.12.03-1.99 1.27-5.62 3.72-.53.36-1.01.54-1.44.53-.47-.01-1.38-.27-2.06-.49-.83-.27-1.49-.42-1.43-.88.03-.24.37-.49 1.02-.75 4.01-1.75 6.69-2.9 8.04-3.47 3.82-1.6 4.62-1.88 5.14-1.89.11 0 .37.03.54.17.14.12.18.28.2.45-.02.07-.02.19-.04.32z"/>
                            </svg>
                            <span class="font-medium">Canal Telegram</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
        <div class="max-w-6xl mx-auto px-[1.2rem] sm:px-6 pt-6 text-center text-xs font-mono text-stone-500 flex flex-col sm:flex-row justify-between items-center gap-2">
            <span>&copy; 2026 {PORTAL_NAME}. Nenhum fato foi distorcido &mdash; o absurdo da realidade brasileira já veio pronto de fábrica.</span>
            <div class="flex items-center space-x-3">
                <a href="{sobre_link}" class="hover:text-stone-300 underline">Aviso Legal (Art. 5º CF/88)</a>
                <span>&bull;</span>
                <a href="{sitemap_link}" class="hover:text-stone-300 underline">Sitemap</a>
                <span>&bull;</span>
                <a href="{sala_link}" class="text-stone-600 hover:text-amber-500/80 transition-colors" title="Sala de Máquinas (Restrito)">⚙️</a>
            </div>
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
                        Narração satírica com voz neural brasileira &bull; Redação ÍMPROBO
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

        // Integração do Mini-Player Sticky Flutuante
        const stickyBar = document.getElementById('sticky-audio-bar');
        if (stickyBar) {
            const stickyPlayBtn = document.getElementById('sticky-play-btn');
            const stickyPlayIcon = document.getElementById('sticky-play-icon');
            const stickyPauseIcon = document.getElementById('sticky-pause-icon');
            const stickyTime = document.getElementById('sticky-time');
            const stickyProgressBar = document.getElementById('sticky-progress-bar');
            const stickyProgressContainer = document.getElementById('sticky-progress-container');
            const stickyCloseBtn = document.getElementById('sticky-close-btn');

            let stickyDismissed = false;

            function syncStickyUI() {
                if (!stickyBar) return;
                if (audio.paused) {
                    stickyPlayIcon.classList.remove('hidden');
                    stickyPauseIcon.classList.add('hidden');
                } else {
                    stickyPlayIcon.classList.add('hidden');
                    stickyPauseIcon.classList.remove('hidden');
                }
                if (stickyTime) {
                    stickyTime.textContent = formatTime(audio.currentTime);
                }
                if (stickyProgressBar && audio.duration) {
                    const pct = (audio.currentTime / audio.duration) * 100;
                    stickyProgressBar.style.width = `${pct}%`;
                }
            }

            audio.addEventListener('timeupdate', syncStickyUI);
            audio.addEventListener('play', syncStickyUI);
            audio.addEventListener('pause', syncStickyUI);

            stickyPlayBtn.addEventListener('click', () => {
                if (audio.paused) {
                    audio.play().catch(e => console.error(e));
                } else {
                    audio.pause();
                }
            });

            if (stickyProgressContainer) {
                stickyProgressContainer.addEventListener('click', (e) => {
                    if (!audio.duration || isNaN(audio.duration)) return;
                    const rect = stickyProgressContainer.getBoundingClientRect();
                    const clickX = e.clientX - rect.left;
                    const pct = Math.max(0, Math.min(1, clickX / rect.width));
                    audio.currentTime = pct * audio.duration;
                    syncStickyUI();
                });
            }

            if (stickyCloseBtn) {
                stickyCloseBtn.addEventListener('click', () => {
                    stickyBar.classList.add('translate-y-full');
                    stickyDismissed = true;
                });
            }

            const mainAudioBox = document.getElementById('article-audio-box');
            if (mainAudioBox && 'IntersectionObserver' in window) {
                const audioObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (stickyDismissed) return;
                        if (!entry.isIntersecting && audio.currentTime > 0) {
                            stickyBar.classList.remove('translate-y-full');
                        } else if (entry.isIntersecting) {
                            stickyBar.classList.add('translate-y-full');
                        }
                    });
                }, { threshold: 0.1 });
                audioObserver.observe(mainAudioBox);

                audio.addEventListener('play', () => {
                    if (stickyDismissed) return;
                    const rect = mainAudioBox.getBoundingClientRect();
                    if (rect.bottom < 0 || rect.top > window.innerHeight) {
                        stickyBar.classList.remove('translate-y-full');
                    }
                });
            }
        }
    });
    </script>
    """

def get_article_target(slug, title=""):
    slug_lower = (slug + " " + title).lower()
    # 1. A República dos Lobistas (Bets, Tigrinho, PEC das praias, Enel, apagão, Faria Lima)
    if "tigrinho" in slug_lower or "bets" in slug_lower or "praias" in slug_lower or "apagao" in slug_lower or "enel" in slug_lower:
        return "republica-lobistas", "A República dos Lobistas", "🎰"
    # 2. A Gazeta das Togas (STF, Pacheco, judiciário, prerrogativas, togas)
    elif "pacheco" in slug_lower or "stf" in slug_lower or "cadeira-vip" in slug_lower or "toga" in slug_lower or "algeminha" in slug_lower or "sindico-supremo" in slug_lower:
        return "gazeta-togas", "A Gazeta das Togas", "⚖️"
    # 3. O Ralo do Orçamento (Emendas Pix, fundão eleitoral, anistia a partidos, cortes de gastos, Centrão)
    elif "anistia" in slug_lower or "fundo-eleitoral" in slug_lower or "centrao" in slug_lower or "orcamento" in slug_lower or "emenda" in slug_lower or "corte-gastos" in slug_lower:
        return "ralo-orcamento", "O Ralo do Orçamento", "💸"
    # 4. O Ringue Eleitoral (Disputa 2026, debates na TV, Lula x Flávio, marqueteiros, pesquisas, 2º turno)
    elif "debate" in slug_lower or "eleic" in slug_lower or "lula" in slug_lower or "flavio" in slug_lower or "bolsonaro" in slug_lower or "marcal" in slug_lower or "concurseiro" in slug_lower or "pendulo" in slug_lower or "sigilo" in slug_lower or "bondade" in slug_lower or "pe-de-meia" in slug_lower or "renan" in slug_lower or "missao" in slug_lower or "6x1" in slug_lower or "salario" in slug_lower or "clt" in slug_lower:
        return "ringue-eleitoral", "O Ringue Eleitoral", "🥊"
    return "comedia-costumes", "Comédia de Costumes", "🎪"

def render_sticky_audio_bar(title):
    safe_title = title.replace('"', '&quot;')
    return f"""
    <!-- Mini-Player de Áudio Sticky Flutuante (Estilo NYT Listen Bar) -->
    <div id="sticky-audio-bar" class="fixed bottom-0 left-0 right-0 z-50 bg-[#FAF9F5] border-t-2 border-t-[#8B0000] shadow-2xl transform translate-y-full transition-transform duration-300 ease-in-out">
        <div class="max-w-4xl mx-auto px-4 py-2 sm:py-2.5 flex items-center justify-between gap-3">
            <div class="flex items-center space-x-3 overflow-hidden">
                <button id="sticky-play-btn" type="button" class="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-[#121212] hover:bg-[#8B0000] text-white flex items-center justify-center shrink-0 transition-colors cursor-pointer" aria-label="Play/Pause">
                    <svg id="sticky-play-icon" class="w-3.5 h-3.5 sm:w-4 sm:h-4 ml-0.5 fill-current" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                    <svg id="sticky-pause-icon" class="w-3.5 h-3.5 sm:w-4 sm:h-4 fill-current hidden" viewBox="0 0 24 24">
                        <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                    </svg>
                </button>
                <div class="overflow-hidden">
                    <div class="flex items-center space-x-1.5">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse shrink-0"></span>
                        <span class="font-mono text-[10px] font-bold uppercase tracking-wider text-[#8B0000]">OUVINDO NO ÍMPROBO</span>
                    </div>
                    <div class="font-serif font-bold text-xs sm:text-sm text-[#121212] truncate max-w-[180px] sm:max-w-md md:max-w-lg">
                        {safe_title}
                    </div>
                </div>
            </div>

            <div class="flex items-center space-x-2.5 sm:space-x-3 shrink-0">
                <!-- Barra de progresso compacta -->
                <div class="hidden sm:block w-28 md:w-44 h-2 bg-[#EBE7DE] rounded-full overflow-hidden cursor-pointer" id="sticky-progress-container" title="Clique para navegar">
                    <div id="sticky-progress-bar" class="h-full bg-[#8B0000] w-0 transition-all duration-75"></div>
                </div>
                <span id="sticky-time" class="font-mono text-xs text-stone-600 min-w-[45px] text-right font-medium">00:00</span>
                <!-- Botão Fechar -->
                <button id="sticky-close-btn" type="button" class="text-stone-500 hover:text-[#121212] p-1 rounded transition-colors cursor-pointer" title="Ocultar mini-player">
                    <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>
    """

def render_share_widget(title, subtitle, slug, frase_disparo_zap=None):
    safe_title = title.replace('"', '\\"').replace("'", "\\'")
    safe_subtitle = subtitle.replace('"', '\\"').replace("'", "\\'")
    safe_zap_phrase = (frase_disparo_zap or "").replace('"', '\\"').replace("'", "\\'").strip()
    return f"""
    <!-- Propague o Deboche: Botão Disparar no Zap da Família & Copiar Link -->
    <div id="share-box" class="my-8 sm:my-10 p-5 sm:p-6 bg-[#FAF9F5] border border-[#D1CEC7] border-l-4 border-l-[#25D366] rounded-sm shadow-xs reveal-on-scroll">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
                <div class="flex items-center space-x-2">
                    <span class="font-mono text-xs uppercase tracking-wider font-bold text-[#128C7E]">PROPAGUE O DEBOCHE</span>
                    <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#EBE7DE] text-stone-700 font-semibold">Munição de Zap</span>
                </div>
                <h4 class="font-serif font-black text-base sm:text-lg text-[#121212] mt-0.5">Disparar no Zap da Família &amp; Redes</h4>
                <p class="font-serif italic text-xs text-stone-600 mt-0.5">
                    Munição retórica pronta para colar nos grupos e passar raiva com categoria.
                </p>
            </div>
            <div class="flex flex-wrap items-center gap-2.5 shrink-0">
                <!-- Botão WhatsApp -->
                <button id="btn-share-zap" type="button" class="inline-flex items-center space-x-2 px-3.5 py-2 bg-[#25D366] hover:bg-[#128C7E] text-white font-mono text-xs font-bold rounded shadow-xs transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] cursor-pointer">
                    <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24">
                        <path d="M17.472 14.382c-.301-.15-1.78-.878-2.056-.979-.276-.1-.476-.15-.676.15-.2.301-.776.979-.952 1.18-.175.2-.351.226-.652.075-.301-.15-1.27-.468-2.42-1.493-.895-.798-1.5-1.784-1.675-2.085-.175-.301-.019-.464.131-.614.136-.135.301-.351.451-.527.151-.175.201-.301.301-.501.101-.2.05-.376-.025-.526-.075-.15-.676-1.63-.927-2.232-.244-.587-.492-.507-.676-.516l-.576-.01c-.2 0-.526.075-.802.376-.276.301-1.052 1.028-1.052 2.508 0 1.48 1.077 2.909 1.228 3.109.15.2 2.12 3.237 5.136 4.54.717.31 1.277.496 1.713.634.72.229 1.375.196 1.893.119.578-.086 1.78-.727 2.03-1.43.251-.702.251-1.304.176-1.43-.076-.126-.276-.201-.577-.351z"/>
                        <path d="M12 2C6.477 2 2 6.477 2 12c0 1.89.525 3.66 1.438 5.168L2 22l4.99-1.408C8.423 21.493 10.155 22 12 22c5.523 0 10-4.477 10-10S17.523 2 12 2zm0 18.167c-1.69 0-3.26-.525-4.56-1.423l-.327-.225-2.964.836.84-2.888-.242-.344C3.784 14.805 3.25 13.447 3.25 12c0-4.825 3.925-8.75 8.75-8.75s8.75 3.925 8.75 8.75-3.925 8.75-8.75 8.75z"/>
                    </svg>
                    <span>Mandar no Zap</span>
                </button>
                <!-- Botão Copiar Link -->
                <button id="btn-copy-link" type="button" class="inline-flex items-center space-x-1.5 px-3 py-2 bg-white border border-[#D1CEC7] hover:border-[#121212] text-stone-800 font-mono text-xs font-bold rounded shadow-xs transition-colors cursor-pointer">
                    <svg id="copy-icon" class="w-4 h-4 fill-current text-stone-600" viewBox="0 0 24 24">
                        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                    </svg>
                    <span id="copy-text">Copiar Link</span>
                </button>
            </div>
        </div>
    </div>
    <script>
    (function() {{
        const btnZap = document.getElementById('btn-share-zap');
        if (btnZap) {{
            btnZap.addEventListener('click', () => {{
                const pageUrl = window.location.href;
                let zapText;
                const zapPhrase = "{safe_zap_phrase}";
                if (zapPhrase && zapPhrase.length > 5) {{
                    zapText = `🚨 *ÍMPROBO | SÁTIRA POLÍTICA:*\\n\\n"${{zapPhrase}}"\\n\\n👉 Leia a análise completa antes que Brasília censure: ${{pageUrl}}`;
                }} else {{
                    zapText = `🚨 *URGENTE NO ÍMPROBO:* {safe_title}\\n\\n"{safe_subtitle}"\\n\\n👉 Leia a crônica completa antes que Brasília censure: ${{pageUrl}}`;
                }}
                const zapUrl = `https://api.whatsapp.com/send?text=${{encodeURIComponent(zapText)}}`;
                window.open(zapUrl, '_blank');
            }});
        }}
        const btnCopy = document.getElementById('btn-copy-link');
        if (btnCopy) {{
            btnCopy.addEventListener('click', () => {{
                navigator.clipboard.writeText(window.location.href).then(() => {{
                    const copyText = document.getElementById('copy-text');
                    const original = copyText.textContent;
                    copyText.textContent = '✓ Link Copiado!';
                    btnCopy.classList.add('border-emerald-600', 'text-emerald-700');
                    setTimeout(() => {{
                        copyText.textContent = original;
                        btnCopy.classList.remove('border-emerald-600', 'text-emerald-700');
                    }}, 2500);
                }}).catch(() => {{
                    const copyText = document.getElementById('copy-text');
                    copyText.textContent = 'Erro ao copiar';
                }});
            }});
        }}
    }})();
    </script>
    """

def render_termometro_widget(slug):
    return f"""
    <!-- Termômetro da Cara de Pau (Enquete Interativa de Cinismo) -->
    <div id="termometro-box" class="my-8 sm:my-10 p-5 sm:p-7 bg-[#FAF9F5] border-2 border-[#121212] rounded-sm shadow-sm reveal-on-scroll">
        <div class="flex items-center justify-between border-b border-[#D1CEC7] pb-3 mb-4">
            <div>
                <span class="font-mono text-xs uppercase tracking-widest font-bold text-[#8B0000]">ENQUETE DE OPINIÃO POPULAR</span>
                <h3 class="font-serif font-black text-lg sm:text-xl text-[#121212] mt-0.5">Termômetro da Cara de Pau</h3>
            </div>
            <span class="text-2xl" title="Medidor Oficial de Óleo de Peroba">🪵</span>
        </div>
        <p class="font-serif italic text-sm text-stone-700 mb-5">
            Na sua sincera avaliação como contribuinte lesado, qual é o nível exato de descaramento deste episódio?
        </p>

        <!-- Opções de Voto -->
        <div id="termometro-opcoes" class="space-y-3">
            <!-- Injetado dinamicamente via JavaScript com persistência em localStorage -->
        </div>

        <div id="termometro-feedback" class="mt-4 pt-3 border-t border-[#D1CEC7] text-xs font-mono text-stone-600 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <span id="termometro-status">Selecione uma opção para registrar seu voto no cartório cínico.</span>
            <span id="termometro-total-votos" class="font-bold text-[#8B0000]"></span>
        </div>
    </div>
    <script>
    (function() {{
        const slug = "{slug}";
        const storageKey = 'improbo_poll_' + slug;

        const OPCOES = [
            {{ id: 1, label: "Nível Bronze", descricao: "Dá pra fingir que não viu se tomar um café bem forte.", baseVotes: 142, emoji: "🥉" }},
            {{ id: 2, label: "Nível Prata", descricao: "É escárnio explícito, mas já virou rotina no Diário Oficial.", baseVotes: 388, emoji: "🥈" }},
            {{ id: 3, label: "Nível Ouro", descricao: "O estoque nacional de óleo de peroba foi zerado em Brasília.", baseVotes: 894, emoji: "🥇" }},
            {{ id: 4, label: "Nível Lendário", descricao: "Nem Maquiavel tendo um pesadelo ousaria tanto cinismo.", baseVotes: 615, emoji: "🔥" }}
        ];

        function renderPoll() {{
            const savedVote = localStorage.getItem(storageKey);
            const container = document.getElementById('termometro-opcoes');
            const statusText = document.getElementById('termometro-status');
            const totalText = document.getElementById('termometro-total-votos');
            if (!container) return;

            let total = OPCOES.reduce((acc, o) => acc + o.baseVotes, 0);
            if (savedVote) {{
                total += 1;
            }}

            if (totalText) {{
                totalText.textContent = total.toLocaleString('pt-BR') + ' votos apurados';
            }}

            if (savedVote) {{
                if (statusText) {{
                    statusText.innerHTML = '✓ <strong>Voto registrado no cartório cínico!</strong> Obrigado por cumprir seu dever cívico.';
                }}
                container.innerHTML = OPCOES.map(op => {{
                    let votes = op.baseVotes + (savedVote == op.id ? 1 : 0);
                    let pct = Math.round((votes / total) * 100);
                    let isUserVote = (savedVote == op.id);
                    return `
                    <div class="p-3 bg-white border ${{isUserVote ? 'border-[#8B0000] ring-1 ring-[#8B0000]' : 'border-[#D1CEC7]'}} rounded-sm relative overflow-hidden termometro-opcao-voted">
                        <div class="absolute top-0 left-0 bottom-0 ${{isUserVote ? 'bg-[#8B0000]/15' : 'bg-[#EBE7DE]/70'}} transition-all duration-700 ease-out" style="width: ${{pct}}%"></div>
                        <div class="relative z-10 flex items-center justify-between gap-3 text-xs sm:text-sm">
                            <div class="flex items-center space-x-2">
                                <span class="text-base">${{op.emoji}}</span>
                                <span class="font-bold text-[#121212] font-serif">${{op.label}}:</span>
                                <span class="text-stone-700 font-serif italic hidden sm:inline">${{op.descricao}}</span>
                                ${{isUserVote ? '<span class="inline-block px-1.5 py-0.2 bg-[#8B0000] text-white text-[10px] font-mono font-bold rounded">SEU VOTO</span>' : ''}}
                            </div>
                            <span class="font-mono font-bold text-stone-800 shrink-0">${{pct}}% (${{votes.toLocaleString('pt-BR')}})</span>
                        </div>
                        <div class="sm:hidden text-[11px] text-stone-600 font-serif italic mt-1 relative z-10">
                            ${{op.descricao}}
                        </div>
                    </div>
                    `;
                }}).join('');
            }} else {{
                if (statusText) {{
                    statusText.textContent = 'Clique em uma das alternativas para registrar sua indignação:';
                }}
                container.innerHTML = OPCOES.map(op => `
                <button type="button" data-poll-id="${{op.id}}" class="termometro-btn termometro-opcao-btn w-full text-left p-3 sm:p-3.5 bg-white border border-[#D1CEC7] hover:border-[#8B0000] hover:shadow-xs rounded-sm transition-all duration-200 cursor-pointer group flex items-start sm:items-center space-x-3">
                    <span class="text-xl group-hover:scale-110 transition-transform shrink-0">${{op.emoji}}</span>
                    <div class="flex-1">
                        <div class="font-serif font-bold text-sm text-[#121212] group-hover:text-[#8B0000] transition-colors">
                            ${{op.label}}
                        </div>
                        <div class="text-xs text-stone-600 font-serif italic">
                            ${{op.descricao}}
                        </div>
                    </div>
                    <span class="hidden sm:inline-block font-mono text-[11px] uppercase tracking-wider text-stone-400 group-hover:text-[#8B0000] font-bold shrink-0">VOTAR &rarr;</span>
                </button>
                `).join('');

                container.querySelectorAll('.termometro-btn').forEach(btn => {{
                    btn.addEventListener('click', () => {{
                        const pollId = btn.getAttribute('data-poll-id');
                        try {{
                            localStorage.setItem(storageKey, pollId);
                        }} catch(e) {{}}
                        renderPoll();
                    }});
                }});
            }}
        }}

        renderPoll();
    }})();
    </script>
    """

def render_newsletter_box(is_article=False, is_sobre=False):
    if is_sobre:
        prefix = "sobre"
    elif is_article:
        prefix = "art"
    else:
        prefix = "home"
    return f"""
    <!-- Newsletter & Canais de Transmissão (Gazeta Semanal do Ímprobo) -->
    <section id="newsletter-box" class="my-8 sm:my-12 p-6 sm:p-8 bg-[#FAF9F5] border-2 border-[#121212] rounded-sm shadow-sm reveal-on-scroll">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            <div class="lg:col-span-7">
                <div class="flex items-center space-x-2 mb-1.5">
                    <span class="bg-[#8B0000] text-white font-mono text-[10px] sm:text-xs font-bold uppercase tracking-widest px-2 py-0.5">GAZETA SEMANAL</span>
                    <span class="font-mono text-xs text-stone-600 uppercase font-semibold">Boletim do Descalabro</span>
                </div>
                <h3 class="font-serif font-black text-xl sm:text-2xl text-[#121212] tracking-tight">
                    Receba as crônicas antes do arquivamento
                </h3>
                <p class="font-serif italic text-sm text-stone-700 mt-1 max-w-xl">
                    Toda semana, um compilado dos maiores absurdos de Brasília mastigados com a ironia que o Diário Oficial esconde. Sem spam, só cinismo de primeira qualidade.
                </p>
                <!-- Formulário de Inscrição -->
                <form id="newsletter-form-{prefix}" class="mt-4 flex flex-col sm:flex-row gap-2 max-w-lg" onsubmit="return false;">
                    <input id="newsletter-email-{prefix}" type="email" required placeholder="Seu melhor e-mail para passar raiva..." class="flex-1 px-3.5 py-2.5 bg-white border border-[#D1CEC7] rounded-sm text-sm text-[#121212] font-sans focus:outline-none focus:border-[#8B0000] transition-colors">
                    <button id="newsletter-btn-{prefix}" type="button" class="px-5 py-2.5 bg-[#121212] hover:bg-[#8B0000] text-white font-mono text-xs uppercase font-bold tracking-wider rounded-sm transition-all duration-200 cursor-pointer shrink-0">
                        Assinar De Graça
                    </button>
                </form>
                <div id="newsletter-msg-{prefix}" class="text-xs font-mono mt-2 hidden"></div>
            </div>

            <!-- Canais Diretos: WhatsApp & Telegram -->
            <div class="lg:col-span-5 border-t lg:border-t-0 lg:border-l border-[#D1CEC7] pt-5 lg:pt-0 lg:pl-8 flex flex-col justify-center">
                <span class="font-mono text-xs uppercase tracking-wider text-stone-600 font-bold mb-2.5 block">
                    Ou siga nossos canais oficiais:
                </span>
                <div class="flex flex-col sm:flex-row lg:flex-col gap-2.5">
                    <a href="{WHATSAPP_CHANNEL_URL}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center justify-between px-3.5 py-2.5 bg-[#25D366]/10 hover:bg-[#25D366]/20 border border-[#25D366]/40 text-[#128C7E] rounded-sm text-xs font-mono font-bold transition-all duration-200 group">
                        <div class="flex items-center space-x-2.5">
                            <svg class="w-4 h-4 fill-current text-[#25D366] shrink-0" viewBox="0 0 24 24">
                                <path d="M12 2C6.477 2 2 6.477 2 12c0 1.89.525 3.66 1.438 5.168L2 22l4.99-1.408C8.423 21.493 10.155 22 12 22c5.523 0 10-4.477 10-10S17.523 2 12 2zm0 18.167c-1.69 0-3.26-.525-4.56-1.423l-.327-.225-2.964.836.84-2.888-.242-.344C3.784 14.805 3.25 13.447 3.25 12c0-4.825 3.925-8.75 8.75-8.75s8.75 3.925 8.75 8.75-3.925 8.75-8.75 8.75z"/>
                            </svg>
                            <span>Canal no WhatsApp</span>
                        </div>
                        <span class="text-stone-400 group-hover:text-[#128C7E] group-hover:translate-x-0.5 transition-transform">&rarr;</span>
                    </a>
                    <a href="{TELEGRAM_CHANNEL_URL}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center justify-between px-3.5 py-2.5 bg-[#229ED9]/10 hover:bg-[#229ED9]/20 border border-[#229ED9]/40 text-[#1d82b3] rounded-sm text-xs font-mono font-bold transition-all duration-200 group">
                        <div class="flex items-center space-x-2.5">
                            <svg class="w-4 h-4 fill-current text-[#229ED9] shrink-0" viewBox="0 0 24 24">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.19-.08-.05-.19-.02-.27 0-.12.03-1.99 1.27-5.62 3.72-.53.36-1.01.54-1.44.53-.47-.01-1.38-.27-2.06-.49-.83-.27-1.49-.42-1.43-.88.03-.24.37-.49 1.02-.75 4.01-1.75 6.69-2.9 8.04-3.47 3.82-1.6 4.62-1.88 5.14-1.89.11 0 .37.03.54.17.14.12.18.28.2.45-.02.07-.02.19-.04.32z"/>
                            </svg>
                            <span>Canal no Telegram</span>
                        </div>
                        <span class="text-stone-400 group-hover:text-[#1d82b3] group-hover:translate-x-0.5 transition-transform">&rarr;</span>
                    </a>
                </div>
            </div>
        </div>
    </section>
    <script>
    (function() {{
        const btn = document.getElementById('newsletter-btn-{prefix}');
        const input = document.getElementById('newsletter-email-{prefix}');
        const msg = document.getElementById('newsletter-msg-{prefix}');
        const storageKey = 'improbo_newsletter_subscribed';

        if (localStorage.getItem(storageKey)) {{
            if (msg) {{
                msg.classList.remove('hidden', 'text-red-600');
                msg.classList.add('text-emerald-700', 'font-bold');
                msg.textContent = '✓ Você já é assinante oficial do Cartório de Ilusões!';
            }}
            if (btn) {{
                btn.textContent = 'Inscrito';
                btn.disabled = true;
                btn.classList.add('opacity-75', 'cursor-not-allowed');
            }}
        }}

        if (btn && input) {{
            btn.addEventListener('click', () => {{
                const email = (input.value || '').trim();
                if (!email || !email.includes('@') || !email.includes('.')) {{
                    msg.classList.remove('hidden', 'text-emerald-700');
                    msg.classList.add('text-red-600', 'font-bold');
                    msg.textContent = 'Por favor, informe um endereço de e-mail válido.';
                    input.focus();
                    return;
                }}

                try {{
                    localStorage.setItem(storageKey, email);
                }} catch(e) {{}}

                msg.classList.remove('hidden', 'text-red-600');
                msg.classList.add('text-emerald-700', 'font-bold');
                msg.textContent = '✓ Inscrição confirmada no Cartório de Ilusões! Em breve você receberá nossos relatórios de descalabro.';
                btn.textContent = 'Inscrito';
                btn.disabled = true;
                btn.classList.add('opacity-75', 'cursor-not-allowed');
                input.disabled = true;
            }});
        }}
    }})();
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
    sticky_audio_html = ""
    audio_script = ""
    if has_audio:
        audio_src = f"../audio/{slug}.mp3"
        audio_player_html = render_audio_player(slug, title, audio_src)
        sticky_audio_html = render_sticky_audio_bar(title)
        audio_script = render_audio_script()

    # Widget de Compartilhamento Viral (Zap da Família & Copiar Link)
    share_widget_html = render_share_widget(title, subtitle, slug, art.get("frase_disparo_zap"))

    # Termômetro da Cara de Pau (Enquete Interativa)
    termometro_widget_html = render_termometro_widget(slug)

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

    safe_title = html.escape(title, quote=True)
    safe_subtitle = html.escape(subtitle, quote=True)
    art_url = f"{PORTAL_URL}/artigos/{slug}.html"
    
    # Resolve absolute image for OG / Twitter Card
    img_abs = f"{PORTAL_URL}/imagens/{slug}.jpg"
    local_img_path = os.path.join(IMAGENS_DIR, f"{slug}.jpg")
    if not os.path.exists(local_img_path):
        capa = art.get("imagem_capa")
        if capa and (capa.startswith("http://") or capa.startswith("https://")):
            img_abs = capa
        else:
            img_abs = f"{PORTAL_URL}/imagens/lula-malabarismo-planalto-centrao.jpg"

    page_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title} | {PORTAL_NAME}</title>
    <meta name="description" content="{safe_subtitle}">
    <link rel="canonical" href="{art_url}">

    <!-- Metatags Sociais Dinâmicas / Open Graph (WhatsApp, Telegram, Facebook) -->
    <meta property="og:type" content="article">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:site_name" content="{PORTAL_NAME}">
    <meta property="og:title" content="{safe_title} | {PORTAL_NAME}">
    <meta property="og:description" content="{safe_subtitle}">
    <meta property="og:url" content="{art_url}">
    <meta property="og:image" content="{img_abs}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="675">

    <!-- Twitter / X Cards (Large Image Preview) -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{safe_title} | {PORTAL_NAME}">
    <meta name="twitter:description" content="{safe_subtitle}">
    <meta name="twitter:image" content="{img_abs}">

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

                <!-- Propague o Deboche: Botão Zap da Família & Copiar Link -->
                {share_widget_html}

                <!-- Termômetro da Cara de Pau (Enquete Interativa) -->
                {termometro_widget_html}

                <!-- Newsletter & Canais de Transmissão -->
                {render_newsletter_box(is_article=True)}

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

    {sticky_audio_html}
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
        filtro_html = ""
        grid_html = ""
    else:
        hero = articles[0]
        hero_slug = hero["slug"]
        hero_title = hero["titulo"]
        hero_subtitle = hero["subtitulo"]
        hero_date = hero.get("data", "Outubro de 2026")
        hero_snippet = hero.get("corpo", [""])[0] if hero.get("corpo") else ""
        hero_img_src, hero_legenda, hero_credito = resolver_imagem_artigo(hero, is_article=False)
        hero_target_id, hero_target_name, hero_icon = get_article_target(hero_slug, hero_title)
        proverbio_dia = PROVERBIOS_BOTEQUIM[(datetime.now().day - 1) % len(PROVERBIOS_BOTEQUIM)]

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
        <section id="hero-article-section" data-alvo="{hero_target_id}" class="article-item bg-white border border-[#D1CEC7] shadow-sm rounded-sm p-6 sm:p-8 md:p-10 mb-8 sm:mb-10 reveal-on-scroll">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-10 items-start">
                <div class="lg:col-span-8">
                    <div class="flex flex-wrap items-center gap-2 mb-3">
                        <span class="bg-[#8B0000] text-white text-xs font-mono font-bold uppercase tracking-wider px-2 py-0.5">MANCHETE PRINCIPAL</span>
                        <span class="text-xs font-mono text-stone-600">{hero_date}</span>
                        <span class="inline-flex items-center space-x-1 text-xs font-mono bg-[#EBE7DE] text-stone-700 px-2 py-0.5 rounded font-medium">
                            <span>{hero_icon}</span>
                            <span>{hero_target_name}</span>
                        </span>
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

                <!-- Editorial Aside Card (#EBE7DE com borda clássica e Gerador de Desculpas) -->
                <div class="lg:col-span-4 bg-[#EBE7DE] p-5 sm:p-6 border-l-4 border-[#121212] font-serif rounded-r-sm shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="font-mono text-xs uppercase tracking-widest text-[#121212] font-bold mb-2">Frase do Dia na Redação</div>
                        <blockquote id="frase-do-dia-texto" class="italic text-[#121212] text-sm md:text-base border-l-2 border-[#8B0000] pl-3 my-2 sm:my-3">
                            &ldquo;{proverbio_dia}&rdquo;
                        </blockquote>
                        <p class="text-xs font-mono text-stone-600 mt-2 sm:mt-3">&mdash; Provérbio de Botequim Parlamentar</p>
                        
                        <div class="mt-4 pt-3 border-t border-[#D1CEC7]">
                            <span class="text-xs font-mono uppercase font-bold text-[#121212] block mb-1">Aviso ao Leitor</span>
                            <p class="text-xs text-stone-700 leading-relaxed font-sans">
                                Se você sentir raiva lendo os fatos, respire fundo. A culpa não é do redator; é do cartório eleitoral que registrou as candidaturas.
                            </p>
                        </div>
                    </div>

                    <!-- Gerador de Desculpas Oficiais de Brasília -->
                    <div class="mt-5 pt-4 border-t border-[#D1CEC7]" id="desculpa-widget">
                        <div class="flex items-center justify-between mb-2">
                            <span class="font-mono text-xs uppercase tracking-widest text-[#8B0000] font-bold flex items-center space-x-1">
                                <span>🏛️ GERADOR DE DESCULPAS</span>
                            </span>
                            <span class="font-mono text-[10px] text-stone-500 uppercase">Gabinete 24h</span>
                        </div>
                        
                        <div id="desculpa-box" class="bg-white border border-[#D1CEC7] p-3 rounded-sm my-2 shadow-2xs min-h-[76px] flex items-center justify-center transition-all duration-300">
                            <p id="desculpa-texto" class="font-serif italic text-xs text-[#121212] text-center leading-snug">
                                &ldquo;A declaração foi tirada de contexto por forças ocultas da oposição para desestabilizar o país.&rdquo;
                            </p>
                        </div>

                        <button id="btn-nova-desculpa" type="button" class="w-full inline-flex items-center justify-center space-x-1.5 py-1.5 px-3 bg-[#121212] hover:bg-[#8B0000] text-white font-mono text-xs font-bold rounded transition-colors cursor-pointer select-none">
                            <svg id="desculpa-spin-icon" class="w-3.5 h-3.5 fill-current transition-transform duration-300" viewBox="0 0 24 24">
                                <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
                            </svg>
                            <span>Sortear Nova Desculpa</span>
                        </button>
                        <p class="font-mono text-[10px] text-stone-500 text-center mt-1.5" id="desculpa-protocolo">
                            Válida perante o STF, CPIs e almoços de domingo.
                        </p>
                    </div>
                </div>
            </div>
        </section>
        """

    # Contagem para os botões de filtro rápido
    target_counts = {}
    for a in articles:
        t_id, _, _ = get_article_target(a["slug"], a.get("titulo", ""))
        target_counts[t_id] = target_counts.get(t_id, 0) + 1

    filtro_html = f"""
        <!-- Filtro Rápido por Editoria Satírica -->
        <div class="mb-8 p-4 sm:p-5 bg-white border border-[#D1CEC7] rounded-sm shadow-xs reveal-on-scroll">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-3">
                <div class="flex items-center space-x-2">
                    <span class="font-mono text-xs uppercase tracking-wider font-bold text-[#8B0000]">EDITORIAS SATÍRICAS DO ÍMPROBO</span>
                    <span class="w-1.5 h-1.5 rounded-full bg-[#8B0000]"></span>
                    <span class="font-serif italic text-xs text-stone-600">Escolha onde o cinismo institucional passa mais vergonha hoje:</span>
                </div>
                <span id="filtro-contador" class="font-mono text-xs text-stone-500 font-medium">Exibindo todas as {len(articles)} crônicas</span>
            </div>
            <div class="flex flex-wrap gap-2" id="filtro-alvos-container">
                <button type="button" data-filter="all" class="filtro-btn active px-3 py-1 font-mono text-xs rounded transition-all cursor-pointer font-bold bg-[#8B0000] text-white shadow-xs">
                    Todas as Crônicas ({len(articles)})
                </button>
                <button type="button" data-filter="ringue-eleitoral" class="filtro-btn px-3 py-1 font-mono text-xs rounded transition-all cursor-pointer font-medium bg-[#EBE7DE] text-stone-800 hover:bg-[#D1CEC7]">
                    🥊 O Ringue Eleitoral ({target_counts.get('ringue-eleitoral', 0)})
                </button>
                <button type="button" data-filter="gazeta-togas" class="filtro-btn px-3 py-1 font-mono text-xs rounded transition-all cursor-pointer font-medium bg-[#EBE7DE] text-stone-800 hover:bg-[#D1CEC7]">
                    ⚖️ A Gazeta das Togas ({target_counts.get('gazeta-togas', 0)})
                </button>
                <button type="button" data-filter="republica-lobistas" class="filtro-btn px-3 py-1 font-mono text-xs rounded transition-all cursor-pointer font-medium bg-[#EBE7DE] text-stone-800 hover:bg-[#D1CEC7]">
                    🎰 A República dos Lobistas ({target_counts.get('republica-lobistas', 0)})
                </button>
                <button type="button" data-filter="ralo-orcamento" class="filtro-btn px-3 py-1 font-mono text-xs rounded transition-all cursor-pointer font-medium bg-[#EBE7DE] text-stone-800 hover:bg-[#D1CEC7]">
                    💸 O Ralo do Orçamento ({target_counts.get('ralo-orcamento', 0)})
                </button>
            </div>
            <div id="filtro-sem-resultados" class="hidden mt-4 pt-3 border-t border-[#D1CEC7] text-center font-serif italic text-stone-500 text-sm">
                Nenhuma crônica encontrada para esta editoria no momento. A assessoria parlamentar deve ter conseguido abafar temporariamente.
            </div>
        </div>
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
            c_target_id, c_target_name, c_icon = get_article_target(a_slug, a_title)
            
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
            <article data-alvo="{c_target_id}" class="article-item article-card-item reveal-on-scroll border border-[#D1CEC7] p-5 bg-white hover:shadow-md transition-all duration-300 flex flex-col justify-between rounded-sm">
                <div>
                    {img_card_html}
                    <div class="flex flex-wrap items-center gap-2 text-xs font-mono mb-2">
                        <span class="text-[#8B0000] font-bold uppercase">{a_cat}</span>
                        <span class="text-[#D1CEC7]">&bull;</span>
                        <span class="text-stone-600">{a_date}</span>
                        <span class="text-[#D1CEC7]">&bull;</span>
                        <span class="inline-flex items-center space-x-1 text-[11px] font-mono bg-[#EBE7DE] text-stone-700 px-1.5 py-0.5 rounded font-medium">{c_icon} {c_target_name}</span>
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
        <section id="grid-articles-section">
            <div class="border-b border-[#121212] pb-2 mb-6 flex items-center justify-between">
                <h2 class="font-serif text-xl sm:text-2xl font-black text-[#121212] tracking-tight">ARQUIVO DA INFÂMIA &bull; OUTRAS CRÔNICAS</h2>
                <span class="font-mono text-xs text-stone-600 uppercase">{len(other_articles)} crônica(s)</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="grid-cards-container">
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

    hero_slug = articles[0]["slug"] if articles else ""
    hero_img_abs = f"{PORTAL_URL}/imagens/{hero_slug}.jpg" if hero_slug else f"{PORTAL_URL}/imagens/lula-malabarismo-planalto-centrao.jpg"
    safe_portal_name = html.escape(PORTAL_NAME, quote=True)
    safe_portal_slogan = html.escape(PORTAL_SLOGAN, quote=True)
    home_desc = "O único jornal que fala a verdade rindo. Crônicas políticas ácidas, sátira mordaz e jornalismo cético sobre o circo de Brasília."
    safe_home_desc = html.escape(home_desc, quote=True)

    page_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_portal_name} | {safe_portal_slogan}</title>
    <meta name="description" content="{safe_home_desc}">
    <link rel="canonical" href="{PORTAL_URL}/">

    <!-- Metatags Sociais Dinâmicas / Open Graph (WhatsApp, Telegram, Facebook) -->
    <meta property="og:type" content="website">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:site_name" content="{safe_portal_name}">
    <meta property="og:title" content="{safe_portal_name} | {safe_portal_slogan}">
    <meta property="og:description" content="{safe_home_desc}">
    <meta property="og:url" content="{PORTAL_URL}/">
    <meta property="og:image" content="{hero_img_abs}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="675">

    <!-- Twitter / X Cards (Large Image Preview) -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{safe_portal_name} | {safe_portal_slogan}">
    <meta name="twitter:description" content="{safe_home_desc}">
    <meta name="twitter:image" content="{hero_img_abs}">

    {COMMON_HEAD_STYLES}
</head>
<body class="min-h-screen flex flex-col justify-between selection:bg-[#8B0000] selection:text-white">
    <div>
        {render_header(is_article=False)}

        <!-- Main Content with NYT Style spacing -->
        <main class="max-w-6xl mx-auto px-[1.2rem] sm:px-6 py-6 sm:py-8">
            {hero_html}
            {filtro_html}
            {grid_html}
            {render_newsletter_box(is_article=False)}
        </main>
    </div>

    {render_footer(is_article=False)}
    {COMMON_SCRIPTS}
</body>
</html>
"""
    return page_html

def generate_sobre_page():
    sobre_url = f"{PORTAL_URL}/sobre.html"
    sobre_img = f"{PORTAL_URL}/imagens/lula-malabarismo-planalto-centrao.jpg"
    safe_portal_name = html.escape(PORTAL_NAME, quote=True)
    safe_desc = "O direito constitucional ao riso, à paródia e à crítica satírica do poder. Fundamentação jurídica nos arts. 5º e 220 da CF/88 e ADPF 130 STF."

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manifesto &amp; Aviso Legal | {safe_portal_name}</title>
    <meta name="description" content="{safe_desc}">
    <link rel="canonical" href="{sobre_url}">

    <!-- Metatags Sociais Dinâmicas / Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:site_name" content="{safe_portal_name}">
    <meta property="og:title" content="Manifesto &amp; Aviso Legal | {safe_portal_name}">
    <meta property="og:description" content="{safe_desc}">
    <meta property="og:url" content="{sobre_url}">
    <meta property="og:image" content="{sobre_img}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="675">

    <!-- Twitter / X Cards -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Manifesto &amp; Aviso Legal | {safe_portal_name}">
    <meta name="twitter:description" content="{safe_desc}">
    <meta name="twitter:image" content="{sobre_img}">

    {COMMON_HEAD_STYLES}
</head>
<body class="min-h-screen flex flex-col justify-between selection:bg-[#8B0000] selection:text-white">
    <div>
        {render_header(is_article=False)}

        <!-- Main Content Sheet -->
        <main class="w-full max-w-4xl mx-auto px-[1.2rem] sm:px-6 my-6 sm:my-10">
            <div class="bg-white border border-[#D1CEC7] shadow-sm rounded-sm p-6 sm:p-10 md:p-14">
                <!-- Header -->
                <div class="mb-8 border-b border-[#D1CEC7] pb-6 reveal-on-scroll">
                    <div class="flex items-center space-x-2 mb-3">
                        <span class="bg-[#8B0000] text-white font-mono text-xs font-bold uppercase tracking-wider px-2.5 py-1">AVISO LEGAL &bull; LINHA EDITORIAL</span>
                        <span class="text-stone-500 font-mono text-xs">Brasília / Brasil</span>
                    </div>
                    <h1 class="article-title font-black text-[#121212] font-serif mb-4">
                        Manifesto Ímprobo: O Direito Constitucional ao Riso e à Paródia Política
                    </h1>
                    <p class="article-subtitle text-stone-700 font-serif italic text-lg leading-relaxed">
                        Por que rir do poder não é apenas um alívio cômico para o cidadão, mas um dever cívico, um remédio contra o autoritarismo e uma garantia democrática inegociável.
                    </p>
                </div>

                <!-- Section 1: Fundamentação Constitucional -->
                <section class="mb-10 reveal-on-scroll">
                    <div class="flex items-center space-x-2 mb-3">
                        <span class="font-mono text-xs font-bold uppercase tracking-wider text-[#8B0000]">01 &bull; NATUREZA JURÍDICA</span>
                        <span class="w-8 h-px bg-[#8B0000]"></span>
                    </div>
                    <h2 class="font-serif font-black text-xl sm:text-2xl text-[#121212] mb-4">
                        Fundamentação na Constituição da República de 1988
                    </h2>
                    <p class="font-serif text-base sm:text-lg text-[#121212]/90 leading-relaxed mb-4">
                        O portal <strong>Ímprobo</strong> exerce sua atividade estritamente respaldado pelos pilares basilares do Estado Democrático de Direito, consagrados na Carta Magna Brasileira de 1988:
                    </p>

                    <div class="space-y-4 my-6">
                        <div class="border-l-4 border-[#8B0000] bg-[#FAF9F5] p-4 sm:p-5 rounded-r-sm">
                            <span class="font-mono text-xs font-bold text-[#8B0000] uppercase block mb-1">Art. 5º, Inciso IV &bull; CF/88</span>
                            <p class="font-serif italic text-stone-800 text-sm sm:text-base leading-relaxed">
                                &ldquo;É livre a manifestação do pensamento, sendo vedado o anonimato.&rdquo;
                            </p>
                        </div>
                        <div class="border-l-4 border-[#8B0000] bg-[#FAF9F5] p-4 sm:p-5 rounded-r-sm">
                            <span class="font-mono text-xs font-bold text-[#8B0000] uppercase block mb-1">Art. 5º, Inciso IX &bull; CF/88</span>
                            <p class="font-serif italic text-stone-800 text-sm sm:text-base leading-relaxed">
                                &ldquo;É livre a expressão da atividade intelectual, artística, científica e de comunicação, independentemente de censura ou licença.&rdquo;
                            </p>
                        </div>
                        <div class="border-l-4 border-[#8B0000] bg-[#FAF9F5] p-4 sm:p-5 rounded-r-sm">
                            <span class="font-mono text-xs font-bold text-[#8B0000] uppercase block mb-1">Art. 220, caput &amp; &sect; 2º &bull; CF/88</span>
                            <p class="font-serif italic text-stone-800 text-sm sm:text-base leading-relaxed">
                                &ldquo;A manifestação do pensamento, a criação, a expressão e a informação, sob qualquer forma, processo ou veículo não sofrerão qualquer restrição [...]. É vedada toda e qualquer censura de natureza política, ideológica e artística.&rdquo;
                            </p>
                        </div>
                    </div>

                    <h3 class="font-serif font-bold text-lg text-[#121212] mt-6 mb-3">
                        Jurisprudência Pacífica do Supremo Tribunal Federal (STF)
                    </h3>
                    <p class="font-serif text-base text-[#121212]/90 leading-relaxed mb-3">
                        A jurisprudência da Suprema Corte brasileira é uníssona em garantir que o humor e a sátira política não constituem ilícito, mas sim instrumento vital de escrutínio popular dos governantes:
                    </p>
                    <ul class="space-y-3 font-sans text-sm text-stone-700 list-disc pl-5">
                        <li>
                            <strong class="text-[#121212]">ADPF 130/DF (Rel. Min. Ayres Britto):</strong> Decisão histórica que revogou em definitivo a Lei de Imprensa da ditadura e consagrou que <em>&ldquo;o humor, a sátira e a caricatura são formas lícitas e salutares de manifestação do pensamento, indispensáveis ao arejamento da vida pública e à desmistificação das liturgias do poder&rdquo;</em>.
                        </li>
                        <li>
                            <strong class="text-[#121212]">ADI 4.451/DF (Rel. Min. Alexandre de Moraes):</strong> Julgamento que declarou inconstitucionais normas que tentavam proibir paródias, charges e piadas sobre políticos, estabelecendo que <em>&ldquo;a liberdade de expressão não resguarda apenas o discurso comedido, elogioso ou dócil, mas tutela igualmente a crítica ácida, mordaz e o escárnio aos agentes públicos no exercício de suas funções&rdquo;</em>.
                        </li>
                    </ul>
                </section>

                <!-- Section 2: Declaração de Paródia e Ficção -->
                <section class="mb-10 pt-8 border-t border-[#D1CEC7] reveal-on-scroll">
                    <div class="flex items-center space-x-2 mb-3">
                        <span class="font-mono text-xs font-bold uppercase tracking-wider text-[#8B0000]">02 &bull; ESCOPO EDITORIAL</span>
                        <span class="w-8 h-px bg-[#8B0000]"></span>
                    </div>
                    <h2 class="font-serif font-black text-xl sm:text-2xl text-[#121212] mb-4">
                        Declaração Explícita de Paródia e Ficção Literária
                    </h2>
                    <p class="font-serif text-base text-[#121212]/90 leading-relaxed mb-4">
                        O <strong>Ímprobo</strong> é um veículo de <strong>crônica satírica, humor político e comédia de costumes</strong>. Todas as nossas matérias operam sob a clássica fórmula dos grandes pasquins brasileiros (como <em>O Pasquim</em>, <em>Sensacionalista</em> e o histórico baronato da imprensa livre):
                    </p>
                    <div class="bg-[#EBE7DE] border-l-4 border-[#121212] p-5 rounded-r-sm my-5 text-sm font-sans leading-relaxed text-[#121212]">
                        <strong>A ANCORAGEM FACTUAL É REAL:</strong> Os temas abordados, projetos de lei, apagões, decisões de cortes, emendas e escândalos políticos noticiados são acontecimentos reais apurados na imprensa pública (G1, Folha de S.Paulo, BBC, Poder360, Agência Brasil). Toda crônica possui um rodapé transparente rotulado <em>&ldquo;O Contexto Real &bull; Rodapé Factual&rdquo;</em> com os fatos crus da apuração jornalística.
                    </div>
                    <div class="bg-[#FAF9F5] border-l-4 border-[#8B0000] p-5 rounded-r-sm my-5 text-sm font-sans leading-relaxed text-[#121212]">
                        <strong>A NARRATIVA É PARÓDIA:</strong> Os diálogos ficcionais, falas atribuídas a personagens, manuais cômicos do otário, deliberações de bastidor e reações hiperbólicas são puras criações de sátira. Nenhuma informação de nossas crônicas deve ser lida como relato jornalístico literal, mas sim como exercício de paródia e ficção humorística.
                    </div>
                </section>

                <!-- Section 3: Caricaturas Editoriais e IA -->
                <section class="mb-10 pt-8 border-t border-[#D1CEC7] reveal-on-scroll">
                    <div class="flex items-center space-x-2 mb-3">
                        <span class="font-mono text-xs font-bold uppercase tracking-wider text-[#8B0000]">03 &bull; ILUSTRAÇÃO &amp; CHARGES</span>
                        <span class="w-8 h-px bg-[#8B0000]"></span>
                    </div>
                    <h2 class="font-serif font-black text-xl sm:text-2xl text-[#121212] mb-4">
                        Caricaturas Digitais por IA no Estilo Clássico
                    </h2>
                    <p class="font-serif text-base text-[#121212]/90 leading-relaxed mb-4">
                        Para preservar a integridade jornalística e homenagear a era de ouro dos quadrinhos e charges editoriais brasileiras, o Ímprobo adota diretrizes estritas de imagem:
                    </p>
                    <ul class="space-y-3 font-sans text-sm text-stone-700 list-disc pl-5">
                        <li>
                            <strong class="text-[#121212]">Zero fotos de agências jornalísticas:</strong> Não utilizamos retratos reais ou fotografias captadas de agências de notícias para fins difamatórios.
                        </li>
                        <li>
                            <strong class="text-[#121212]">Caricaturas autorais geradas por IA:</strong> Nossas charges são geradas por modelos de Inteligência Artificial no estilo de charge editorial dos anos 70/80 (nanquim expressivo, aquarela e guache vibrante), satirizando comportamentos e situações públicas em tom de pastelão cômico.
                        </li>
                        <li>
                            <strong class="text-[#121212]">Zero marcas ou logotipos de terceiros:</strong> Não incluímos marcas registradas, títulos ou logotipos comerciais de revistas externas. Nossas ilustrações trazem o crédito formal: <em>&ldquo;Arte: Caricatura Editorial IA / Ilustração Satírica&rdquo;</em>.
                        </li>
                    </ul>
                </section>

                <!-- Section 4: Acessibilidade e Voz Neural -->
                <section class="mb-10 pt-8 border-t border-[#D1CEC7] reveal-on-scroll">
                    <div class="flex items-center space-x-2 mb-3">
                        <span class="font-mono text-xs font-bold uppercase tracking-wider text-[#8B0000]">04 &bull; ACESSIBILIDADE</span>
                        <span class="w-8 h-px bg-[#8B0000]"></span>
                    </div>
                    <h2 class="font-serif font-black text-xl sm:text-2xl text-[#121212] mb-4">
                        Jornalismo Acessível &bull; Narração Neural em Áudio
                    </h2>
                    <p class="font-serif text-base text-[#121212]/90 leading-relaxed mb-4">
                        Todas as crônicas do portal contam com versão narrada em áudio neural em português brasileiro (Edge-TTS), garantindo acesso irrestrito para pessoas com deficiência visual, pessoas em trânsito e leitores que preferem acompanhar o noticiário cínico em formato de podcast.
                    </p>
                </section>

                <!-- Section 5: Expediente e Contato -->
                <section class="mb-8 pt-8 border-t border-[#D1CEC7] reveal-on-scroll">
                    <div class="flex items-center space-x-2 mb-3">
                        <span class="font-mono text-xs font-bold uppercase tracking-wider text-[#8B0000]">05 &bull; EXPEDIENTE &amp; REDAÇÃO</span>
                        <span class="w-8 h-px bg-[#8B0000]"></span>
                    </div>
                    <h2 class="font-serif font-black text-xl sm:text-2xl text-[#121212] mb-4">
                        Quem Faz o Ímprobo
                    </h2>

                    <!-- Author Bio Card em Sobre -->
                    <div class="author-bio-card-sobre mb-8 p-5 sm:p-6 bg-[#FAF9F5] border-2 border-[#121212] rounded-sm shadow-sm flex flex-col sm:flex-row items-center sm:items-start gap-5">
                        <div class="relative shrink-0">
                            <img src="imagens/autor.png" alt="Caricatura de Pavi - Diretor Editorial &amp; Fundador" class="w-20 h-20 sm:w-24 sm:h-24 rounded-full object-cover object-center border-2 border-[#8B0000] shadow-md bg-[#EBE7DE]" loading="lazy">
                            <span class="absolute -bottom-1 -right-1 bg-[#8B0000] text-white text-[9px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded shadow-xs">AUTOR</span>
                        </div>
                        <div class="flex-1 text-center sm:text-left">
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1.5">
                                <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2">
                                    <h3 class="font-serif font-black text-xl text-[#121212] tracking-tight">Pavi</h3>
                                    <span class="text-stone-400 hidden sm:inline">&bull;</span>
                                    <span class="font-mono text-xs text-[#8B0000] font-bold uppercase tracking-wider">Diretor Editorial &amp; Fundador</span>
                                </div>
                                <span class="text-[11px] font-mono text-stone-500 uppercase">Brasília / Brasil</span>
                            </div>
                            <p class="font-serif italic text-stone-800 text-sm sm:text-base leading-relaxed">
                                &ldquo;Entusiasta de jornalismo independente, tecnologia e crônica política. Acredita que a sátira não é apenas diversão, mas o único escudo democrático contra a arrogância de quem manda. Escreve e programa para lembrar aos governantes que o rei está sempre nu.&rdquo;
                            </p>
                        </div>
                    </div>

                    <h3 class="font-serif font-bold text-lg text-[#121212] mb-3">
                        Contato com a Redação Ácida
                    </h3>
                    <p class="font-serif text-base text-[#121212]/90 leading-relaxed mb-6">
                        Dúvidas, pedidos de retificação factual, sugestões de descalabros a investigar ou denúncias de políticos agindo com excesso de decoro podem ser encaminhados aos nossos canais:
                    </p>

                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                        <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" class="p-4 bg-[#FAF9F5] border border-[#D1CEC7] hover:border-[#121212] rounded-sm text-center transition-all group">
                            <span class="font-mono text-xs uppercase font-bold text-[#8B0000] block mb-1">Instagram</span>
                            <span class="font-serif font-bold text-sm text-[#121212] group-hover:text-[#8B0000]">{INSTAGRAM_HANDLE}</span>
                        </a>
                        <a href="{WHATSAPP_CHANNEL_URL}" target="_blank" rel="noopener noreferrer" class="p-4 bg-[#FAF9F5] border border-[#D1CEC7] hover:border-[#121212] rounded-sm text-center transition-all group">
                            <span class="font-mono text-xs uppercase font-bold text-[#25D366] block mb-1">WhatsApp</span>
                            <span class="font-serif font-bold text-sm text-[#121212] group-hover:text-[#25D366]">Canal Oficial</span>
                        </a>
                        <a href="{TELEGRAM_CHANNEL_URL}" target="_blank" rel="noopener noreferrer" class="p-4 bg-[#FAF9F5] border border-[#D1CEC7] hover:border-[#121212] rounded-sm text-center transition-all group">
                            <span class="font-mono text-xs uppercase font-bold text-[#229ED9] block mb-1">Telegram</span>
                            <span class="font-serif font-bold text-sm text-[#121212] group-hover:text-[#229ED9]">Canal Oficial</span>
                        </a>
                    </div>

                    <!-- Newsletter no Sobre -->
                    {render_newsletter_box(is_article=False, is_sobre=True)}

                    <div class="mt-8 pt-6 border-t border-[#D1CEC7] flex justify-between items-center">
                        <a href="index.html" class="neo-link font-mono text-xs uppercase tracking-wider text-[#8B0000] font-bold inline-flex items-center space-x-1">
                            <span>&larr;</span>
                            <span>Voltar à Capa Principal</span>
                        </a>
                        <span class="font-mono text-xs text-stone-500">Brasília &bull; 2026</span>
                    </div>
                </section>
            </div>
        </main>
    </div>

    {render_footer(is_article=False)}
    {COMMON_SCRIPTS}
</body>
</html>
"""

def generate_sitemap(articles):
    today = datetime.now().strftime("%Y-%m-%d")
    xml_entries = [
        f"""  <url>
    <loc>{PORTAL_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""",
        f"""  <url>
    <loc>{PORTAL_URL}/sobre.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>"""
    ]

    for art in articles:
        slug = art.get("slug", "")
        ts = art.get("timestamp") or art.get("data_iso")
        if ts and "T" in str(ts):
            mod_date = str(ts).split("T")[0]
        else:
            mod_date = today
        xml_entries.append(f"""  <url>
    <loc>{PORTAL_URL}/artigos/{slug}.html</loc>
    <lastmod>{mod_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(xml_entries)}
</urlset>
"""
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    print(f"Sitemap gerado: {SITEMAP_PATH}")

def generate_robots():
    robots_content = f"""User-agent: *
Disallow: /sala-de-maquinas
Disallow: /sala-de-maquinas.html
Allow: /

Sitemap: {PORTAL_URL}/sitemap.xml
"""
    with open(ROBOTS_PATH, "w", encoding="utf-8") as f:
        f.write(robots_content)
    print(f"Robots gerado: {ROBOTS_PATH}")

def create_vercel_config():
    config = {
        "framework": None,
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
    os.makedirs(IMAGENS_DIR, exist_ok=True)
    articles = load_articles()
    print(f"Encontrados {len(articles)} artigos em {CONTENT_DIR}")

    # Generate individual article HTMLs
    for art in articles:
        slug = art["slug"]
        out_path = os.path.join(ARTIGOS_DIR, f"{slug}.html")
        html_content = generate_article_page(art)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Artigo gerado: {out_path}")

    # Generate index.html
    home_html = generate_home_page(articles)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(home_html)
    print(f"Home gerada: {INDEX_PATH}")

    # Generate sobre.html
    sobre_html = generate_sobre_page()
    with open(SOBRE_PATH, "w", encoding="utf-8") as f:
        f.write(sobre_html)
    print(f"Página Sobre gerada: {SOBRE_PATH}")

    # Generate sala-de-maquinas.html
    try:
        from sala_maquinas import generate_sala_de_maquinas_page
        sala_html = generate_sala_de_maquinas_page(articles, PORTAL_URL)
        sala_path = os.path.join(BASE_DIR, "sala-de-maquinas.html")
        with open(sala_path, "w", encoding="utf-8") as f:
            f.write(sala_html)
        print(f"Sala de Máquinas gerada: {sala_path}")
    except Exception as e:
        print(f"[!] Erro ao gerar Sala de Máquinas: {e}")

    # Generate sitemap.xml & robots.txt
    generate_sitemap(articles)
    generate_robots()

    # Generate vercel.json
    create_vercel_config()
    print("Build Ímprobo Produção finalizado com sucesso!")

if __name__ == "__main__":
    build_all()

