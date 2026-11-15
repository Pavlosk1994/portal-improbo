#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO DE GERAÇÃO DE CARDS SOCIAIS TIPOGRÁFICOS (OPEN GRAPH / WHATSAPP / TWITTER)
Gera imagens 1200x675 de altíssima qualidade em milissegundos com Pillow:
- Papel creme editorial clássico (#F4F1EA)
- Moldura dupla jornalística (New York Times style)
- Cabeçalho com logo ÍMPROBO e data
- Manchete em tipografia serifada monumental
- Subtítulo e Frase de Impacto (Soundbite)
- Carimbo burocrático satírico com textura de tinta desgastada
100% offline, custo zero, sem limites de cota, sem bloqueios de IA.
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGENS_DIR = os.path.join(BASE_DIR, "imagens")

# Fontes do sistema Linux
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def carregar_fonte(caminho, tamanho, fallback_padrao=None):
    try:
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    except Exception:
        pass
    return ImageFont.load_default()

def selecionar_carimbo_satiro(categoria="", titulo=""):
    cat = (categoria or "").lower()
    tit = (titulo or "").lower()
    
    if "toga" in cat or "stf" in tit or "supremo" in tit or "ministro" in tit:
        return "DECISÃO MONOCRÁTICA", "#8B0000"
    elif "ringue" in cat or "eleiç" in cat or "lula" in tit or "bolsonaro" in tit:
        return "URGÊNCIA ELEITORAL", "#8B0000"
    elif "lobista" in cat or "emenda" in tit or "centrão" in tit or "congresso" in tit:
        return "BALCÃO OFICIAL", "#121212"
    elif "orçamento" in cat or "imposto" in tit or "haddad" in tit or "corte" in tit:
        return "LEI DO BOLETO", "#8B0000"
    else:
        return "CARA DE PAU HOMOLOGADA", "#8B0000"

def gerar_card_social(dados_artigo, forcar=False):
    """
    Gera o card social tipográfico (1200x675) para o artigo.
    Salva em imagens/{slug}.jpg
    """
    slug = dados_artigo.get("slug")
    if not slug:
        return None

    os.makedirs(IMAGENS_DIR, exist_ok=True)
    caminho_final = os.path.join(IMAGENS_DIR, f"{slug}.jpg")

    # Se já existir e não for forçado, não regera
    if os.path.exists(caminho_final) and not forcar:
        return caminho_final

    titulo = dados_artigo.get("titulo", "ÍMPROBO").strip()
    subtitulo = dados_artigo.get("subtitulo", "").strip()
    frase_zap = dados_artigo.get("frase_disparo_zap", "").strip()
    categoria = dados_artigo.get("categoria", "Crônica Política").strip()
    data = dados_artigo.get("data", "Novembro de 2026").strip()

    # Dimensões exatas Open Graph / Twitter Card Large
    W, H = 1200, 675
    img = Image.new("RGB", (W, H), color="#F4F1EA")
    draw = ImageDraw.Draw(img)

    # 1. Moldura Editorial Dupla Clássica (The New York Times / Broadside)
    # Borda externa fina
    draw.rectangle([20, 20, W - 20, H - 20], outline="#121212", width=2)
    # Borda interna dupla
    draw.rectangle([26, 26, W - 26, H - 26], outline="#D1CEC7", width=1)
    draw.rectangle([32, 32, W - 32, H - 32], outline="#121212", width=1)

    # 2. Cabeçalho de Imprensa (Masthead)
    fonte_logo = carregar_fonte(SERIF_BOLD, 46)
    fonte_mono = carregar_fonte(MONO_BOLD, 15)
    fonte_serif_sm = carregar_fonte(SERIF_ITALIC, 16)

    # Linha divisória do topo
    draw.line([50, 105, W - 50, 105], fill="#121212", width=2)
    draw.line([50, 109, W - 50, 109], fill="#121212", width=1)

    # Nome do jornal centralizado no cabeçalho
    draw.text((55, 48), "Í M P R O B O", fill="#121212", font=fonte_logo)
    
    # Subtítulo institucional
    draw.text((360, 62), "JORNALISMO SATÍRICO & CRÔNICA POLÍTICA", fill="#555555", font=fonte_mono)

    # Metadados topo direita
    draw.text((W - 350, 62), f"{data.upper()} | BRASÍLIA", fill="#121212", font=fonte_mono)

    # 3. Kicker / Chapéu com Badge da Editoria
    fonte_badge = carregar_fonte(SANS_BOLD, 14)
    # Caixa da categoria
    cat_texto = f"  {categoria.upper()}  "
    draw.rectangle([55, 125, 55 + len(cat_texto) * 11, 152], fill="#8B0000")
    draw.text((62, 131), cat_texto.strip(), fill="#FFFFFF", font=fonte_badge)

    # 4. Carimbo Burocrático Satírico no Topo Direito
    texto_carimbo, cor_carimbo = selecionar_carimbo_satiro(categoria, titulo)
    # Desenha carimbo estilizado em imagem separada para rotacionar
    carimbo_w, carimbo_h = 320, 50
    carimbo_img = Image.new("RGBA", (carimbo_w, carimbo_h), (255, 255, 255, 0))
    carimbo_draw = ImageDraw.Draw(carimbo_img)
    carimbo_draw.rectangle([2, 2, carimbo_w - 4, carimbo_h - 4], outline=cor_carimbo, width=3)
    carimbo_draw.rectangle([6, 6, carimbo_w - 8, carimbo_h - 8], outline=cor_carimbo, width=1)
    fonte_carimbo = carregar_fonte(MONO_BOLD, 16)
    
    # Centraliza texto no carimbo
    carimbo_draw.text((18, 16), f"★ {texto_carimbo} ★", fill=cor_carimbo, font=fonte_carimbo)
    # Rotaciona -4 graus
    carimbo_rot = carimbo_img.rotate(4, expand=True, resample=Image.BICUBIC)
    img.paste(carimbo_rot, (W - 380, 115), carimbo_rot)

    # 5. Manchete Monumental (H1)
    # Ajusta tamanho da fonte com base no comprimento do título
    len_t = len(titulo)
    if len_t < 45:
        size_h1 = 52
        wrap_w = 26
    elif len_t < 70:
        size_h1 = 44
        wrap_w = 32
    else:
        size_h1 = 38
        wrap_w = 38

    fonte_h1 = carregar_fonte(SERIF_BOLD, size_h1)
    linhas_titulo = textwrap.wrap(titulo, width=wrap_w)

    y_pos = 175
    for linha in linhas_titulo[:3]:
        draw.text((55, y_pos), linha, fill="#121212", font=fonte_h1)
        y_pos += size_h1 + 10

    # Linha divisória fina sob o título
    y_pos += 10
    draw.line([55, y_pos, W - 55, y_pos], fill="#D1CEC7", width=1)
    y_pos += 20

    # 6. Frase de Impacto / Soundbite (Olho de Texto com Aspas Monumentais)
    if frase_zap or subtitulo:
        texto_destaque = frase_zap if frase_zap else subtitulo
        # Aspas vermelhas gigantes
        fonte_aspas = carregar_fonte(SERIF_BOLD, 75)
        draw.text((55, y_pos - 15), "“", fill="#8B0000", font=fonte_aspas)

        fonte_quote = carregar_fonte(SERIF_ITALIC, 24)
        linhas_quote = textwrap.wrap(texto_destaque, width=54)
        y_quote = y_pos + 10
        for lq in linhas_quote[:2]:
            draw.text((105, y_quote), lq, fill="#252525", font=fonte_quote)
            y_quote += 32

    # 7. Rodapé do Card
    draw.line([50, H - 75, W - 50, H - 75], fill="#121212", width=1)
    draw.line([50, H - 71, W - 50, H - 71], fill="#121212", width=2)

    fonte_footer = carregar_fonte(MONO_BOLD, 14)
    draw.text((55, H - 55), "PORTAL-IMPROBO.VERCEL.APP", fill="#8B0000", font=fonte_footer)
    draw.text((430, H - 55), "• EDIÇÃO COMPLETA COM ÁUDIO NEURAL •", fill="#555555", font=fonte_footer)
    draw.text((W - 320, H - 55), "LENTE CÍNICA 100% CALIBRADA", fill="#121212", font=fonte_footer)

    # Salva imagem JPEG de alta qualidade
    img.save(caminho_final, "JPEG", quality=92, optimize=True)
    print(f"[✓] Card social gerado com sucesso: {caminho_final} ({os.path.getsize(caminho_final)} bytes)")
    return caminho_final

if __name__ == "__main__":
    import sys
    import json
    
    # Teste rápido se chamado diretamente
    artigo_teste = {
        "slug": "teste-card-social-improbo",
        "titulo": "O RINGUE DA CARA DE PAU: LULA E FLÁVIO NO VALE-TUDO DA TV",
        "subtitulo": "Candidatos trocam gentilezas com afeto de quem disputa a última vaga no bote de Chernobyl.",
        "frase_disparo_zap": "O debate na TV provou que a política brasileira não precisa de inteligência artificial; a burrice natural já é imbatível.",
        "categoria": "🥊 O Ringue Eleitoral",
        "data": "14 de Novembro de 2026"
    }
    gerar_card_social(artigo_teste, forcar=True)
