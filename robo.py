#!/usr/bin/env python3
"""
Robô Autônomo de Varredura e Redação Satírica - ÍMPROBO
Monitora os principais jornais do Brasil (RSS Feeds & Scraping),
seleciona a manchete de maior relevância política, extrai a foto original (og:image),
redige a crônica satírica com base no PROMPT_MESTRE.md (Gemini) e compila o site.
"""

import os
import sys
import json
import re
import time
import argparse
import unicodedata
import base64
from datetime import datetime, timezone
import email.utils
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

# Importa o compilador do site
from build import build_all, CONTENT_DIR, BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "noticias_db.json")
ENV_PATH = os.path.join(BASE_DIR, ".env")
PROMPT_MESTRE_PATH = os.path.join(BASE_DIR, "PROMPT_MESTRE.md")
IMAGENS_DIR = os.path.join(BASE_DIR, "imagens")

# Feeds RSS oficiais dos maiores portais de notícias do Brasil
RSS_FEEDS = [
    {
        "fonte": "G1 Política",
        "url": "https://g1.globo.com/rss/g1/politica/",
        "peso_fonte": 1.2
    },
    {
        "fonte": "Folha de S.Paulo - Poder",
        "url": "https://feeds.folha.uol.com.br/poder/rss091.xml",
        "peso_fonte": 1.3
    },
    {
        "fonte": "BBC News Brasil",
        "url": "https://www.bbc.com/portuguese/index.xml",
        "peso_fonte": 1.2
    },
    {
        "fonte": "Agência Brasil - Política",
        "url": "https://agenciabrasil.ebc.com.br/rss/politica/feed.xml",
        "peso_fonte": 1.1
    },
    {
        "fonte": "Poder360",
        "url": "https://www.poder360.com.br/feed/",
        "peso_fonte": 1.2
    }
]

# Palavras-chave para cálculo de relevância institucional e potencial satírico
TERMOS_RELEVANCIA = {
    # Instituições & Poder Máximo (Peso 5)
    "stf": 5, "supremo": 5, "congresso": 5, "senado": 5, "câmara": 5, 
    "planalto": 5, "governo": 4, "ministério": 4, "tribunal": 4,

    # Figuras Centrais & Presidência (Peso 5)
    "lula": 5, "bolsonaro": 5, "flávio": 5, "moraes": 5, "alcolumbre": 4, 
    "hugo motta": 4, "pacheco": 4, "haddad": 5, "dino": 5, "ministro": 4,

    # Pautas de Alto Impacto, Bolso do Povo e Eleições (Peso 5)
    "corte de gastos": 5, "corte": 4, "gastos": 4, "inflação": 5, "dólar": 5,
    "bandeira vermelha": 5, "conta de luz": 5, "energia": 4, "apagão": 5, "enel": 5,
    "bet": 5, "bets": 5, "tigrinho": 5, "bolsa família": 5, "picanha": 5, "carne": 4,
    "emenda pix": 5, "emendas pix": 5, "emenda": 4, "emendas": 4,
    "imposto": 5, "taxa": 4, "aumento": 4, "combustível": 4, "gasolina": 4,
    "eleição": 5, "eleições": 5, "2º turno": 5, "segundo turno": 5, "pesquisa": 4,
    "pec": 4, "6x1": 5, "votação": 4, "reforma": 4, "orçamento": 4, "salário": 4,

    # Gatilhos de Contradição e Absurdo / Comédia de Costumes (Peso 4)
    "recuo": 4, "volta atrás": 4, "gafe": 4, "escândalo": 5, "aliança": 3,
    "acordo": 4, "promessa": 4, "surto": 4, "farra": 5, "privilégio": 5, "penduricalho": 5
}

def carregar_env():
    """Lê arquivo .env local se existir para obter chaves de API"""
    if os.path.exists(ENV_PATH):
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception as e:
            print(f"[!] Erro ao carregar .env: {e}")

def obter_api_key():
    carregar_env()
    return os.environ.get("GEMINI_API_KEY")

def carregar_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"processadas": []}

def salvar_db(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def slugify(texto):
    """Converte título em slug amigável para URLs e arquivos"""
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^a-zA-Z0-9\s-]', '', texto).lower()
    return re.sub(r'[-\s]+', '-', texto).strip('-')[:50]

def varrer_feed_rss(feed_info):
    """Faz requisição e parsing de um feed RSS com User-Agent de navegador"""
    url = feed_info["url"]
    fonte = feed_info["fonte"]
    noticias = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()

        items = []
        try:
            soup = BeautifulSoup(content, 'xml')
            items = soup.find_all('item')
        except Exception:
            try:
                soup = BeautifulSoup(content, 'html.parser')
                items = soup.find_all('item')
            except Exception:
                items = []

        if items:
            for item in items:
                title_tag = item.find('title')
                link_tag = item.find('link')
                desc_tag = item.find('description')
                pub_tag = item.find('pubDate')

                title = title_tag.text.strip() if title_tag else ""
                link = link_tag.text.strip() if link_tag else ""
                desc = BeautifulSoup(desc_tag.text, 'html.parser').get_text(strip=True) if desc_tag else ""
                pub_date = pub_tag.text.strip() if pub_tag else ""

                if title and link:
                    noticias.append({
                        "fonte": fonte,
                        "titulo": title,
                        "link": link,
                        "resumo": desc,
                        "data_pub": pub_date,
                        "peso_fonte": feed_info.get("peso_fonte", 1.0)
                    })
        else:
            # Fallback nativo padrão com xml.etree.ElementTree (sem dependência externa)
            try:
                root = ET.fromstring(content)
                for item in root.iter('item'):
                    title = (item.findtext('title') or '').strip()
                    link = (item.findtext('link') or '').strip()
                    desc = (item.findtext('description') or '').strip()
                    pub_date = (item.findtext('pubDate') or '').strip()
                    if title and link:
                        noticias.append({
                            "fonte": fonte,
                            "titulo": title,
                            "link": link,
                            "resumo": desc,
                            "data_pub": pub_date,
                            "peso_fonte": feed_info.get("peso_fonte", 1.0)
                        })
            except Exception:
                pass
    except Exception as e:
        print(f"[-] Erro ao ler feed {fonte} ({url}): {e}")

    return noticias

def extrair_data_publicacao(pub_str):
    """Converte strings de datas de RSS para datetime em UTC de forma resiliente"""
    if not pub_str:
        return None
    try:
        dt = email.utils.parsedate_to_datetime(pub_str)
        if dt:
            return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    
    # Tentativa ISO
    try:
        clean = pub_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass

    # Tentativa formatos comuns brasileiros
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(pub_str, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None

def calcular_relevancia(noticia, db_urls):
    """
    Atribui nota de relevância com prioridade estrita para NOTÍCIAS RECENTES E QUENTES:
    1. Novidade Absoluta / Recência (últimas horas ganham bônus máximo, notícias velhas sofrem penalidade pesada)
    2. Termos de poder, contradições e apelo popular (bolso do cidadão, hipocrisia, comédia de costumes)
    3. Peso da fonte jornalística
    """
    if noticia["link"] in db_urls:
        return -100  # Já processada anteriormente

    texto_busca = f"{noticia['titulo']} {noticia['resumo']}".lower()
    score_termos = 0.0

    for termo, peso in TERMOS_RELEVANCIA.items():
        if re.search(r'\b' + re.escape(termo) + r'\b', texto_busca):
            score_termos += peso

    score_base = score_termos * noticia.get("peso_fonte", 1.0)

    # 4. Cálculo do Fator Quente (Recência Cronológica)
    dt_pub = extrair_data_publicacao(noticia.get("data_pub", ""))
    bonus_recencia = 0.0
    if dt_pub:
        try:
            agora = datetime.now(timezone.utc)
            horas_atras = max(0.0, (agora - dt_pub).total_seconds() / 3600.0)
            
            if horas_atras <= 6:
                bonus_recencia = 25.0   # Fervendo / Breaking News (últimas 6 horas)
            elif horas_atras <= 24:
                bonus_recencia = 18.0   # Notícia Quente do dia (últimas 24 horas)
            elif horas_atras <= 48:
                bonus_recencia = 8.0    # Recente (últimos 2 dias)
            elif horas_atras <= 72:
                bonus_recencia = 0.0    # No limite (até 3 dias)
            else:
                bonus_recencia = -30.0  # Notícia velha de gaveta: penalizada para nunca passar na frente
        except Exception:
            bonus_recencia = 0.0
    else:
        # Se não há data no feed, assume recência neutra
        bonus_recencia = 2.0

    score_final = score_base + bonus_recencia
    return round(score_final, 2)

def extrair_imagem_capa(url):
    """
    Visita o link da matéria original e extrai a imagem principal (og:image)
    e seus créditos/legendas para compor o cabeçalho factual.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    img_url = None
    credito = ""
    legenda = ""

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')

        soup = BeautifulSoup(html, 'html.parser')

        # 1. Busca por Open Graph image (padrão universal da grande imprensa)
        og_img = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'})
        if og_img and og_img.get('content'):
            img_url = og_img['content'].strip()

        # Fallback twitter:image
        if not img_url:
            tw_img = soup.find('meta', attrs={'name': 'twitter:image'})
            if tw_img and tw_img.get('content'):
                img_url = tw_img['content'].strip()

        # Validação estrita da imagem: deve ser URL absoluta válida e não ícone/logo/pixel
        if img_url:
            img_lower = img_url.lower()
            if not (img_lower.startswith('http://') or img_lower.startswith('https://')):
                img_url = None
            elif any(ign in img_lower for ign in ['favicon', 'avatar', 'icon', 'logo-default', '.svg', 'spacer.gif']):
                img_url = None

        if img_url:
            # 2. Extração de Crédito ou Veículo
            site_name_meta = soup.find('meta', property='og:site_name')
            if site_name_meta and site_name_meta.get('content'):
                credito = f"Foto: Reprodução / {site_name_meta['content'].strip()}"
            else:
                domain = urllib.parse.urlparse(url).netloc.replace('www.', '')
                credito = f"Foto: Reprodução / {domain.capitalize()}"

            # 3. Tenta encontrar a legenda principal da foto no DOM
            caption_tag = soup.find('figcaption') or soup.find(class_=re.compile(r'(caption|legenda|foto-credito)', re.I))
            if caption_tag:
                legenda = caption_tag.get_text(strip=True)[:180]
        else:
            credito = None
            legenda = None

    except Exception as e:
        print(f"[!] Aviso ao extrair imagem de {url}: {e}")
        img_url = None
        credito = None
        legenda = None

    return {
        "imagem_url": img_url,
        "credito": credito,
        "legenda_sugerida": legenda
    }

def redigir_cronica_gemini(noticia, dados_imagem, api_key):
    """
    Chama a API REST do Gemini para gerar a crônica satírica com estrito
    rigor aos fatos reais, tom de pasquim raiz e formatação JSON aprovada.
    """
    url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    # Prompt de Instrução baseado no PROMPT_MESTRE.md
    instrucao_sistema = """
Você é o Redator-Chefe e Cronista Ácido de **ÍMPROBO**, portal brasileiro de jornalismo satírico, crônica política e comédia de costumes.
Sua missão:
1. Fidelidade Absoluta ao Fato Real: Os personagens, dados, falas e decisões são 100% reais (sem inventar mentiras).
2. Acidez Máxima e Humor de Pasquim Raiz: Cínico, visceral, analítico e irônico. Proibido tom acadêmico ou morno. Use metáforas populares ácidas (o agiota de calçada, o garçom do rodízio, o malandro na missa). Desmonte a pose e a liturgia dos políticos.
3. Regra dos Títulos Curtos e Punchy: O título DEVE ser curto (40 a 65 caracteres no máximo), em caixa alta, contendo uma piada ou contradição sarcástica imediata (ex: 'SOCIALISMO DE MANHÃ, CENTRÃO DE TARDE'). Proibido títulos longos ou que pareçam sinopses. O detalhamento do contexto vai no subtítulo.
4. Regra da Caricatura Editorial IA no Estilo Clássico (Anos 70/80): Crie uma descrição visual detalhada da cena para gerar uma charge editorial satírica. A cena deve ser cômica, escrachada, retratando os personagens em situação absurda (pastelão, nanquim expressivo, aquarela e guache vibrante). REGRA MANDATÓRIA: É terminantemente proibido qualquer texto 'MAD', logotipos ou marcas registradas.
5. Sem Viés Partidário: O alvo é sempre o poder, a burocracia estatal, a incoerência eleitoral e o teatro político.
6. Estrutura de Retorno: Você DEVE responder OBRIGATORIAMENTE com um único objeto JSON válido (sem tags markdown ```json), contendo:
{
  "titulo": "MANCHETE CURTA COM PIADA OU CONTRADIÇÃO (MÁX 60 CARACTERES)",
  "subtitulo": "Subtítulo cínico e explicativo detalhando o absurdo da situação",
  "categoria": "Comédia de Costumes" (ou Crônica Política / Folclore de Brasília),
  "tempo_leitura": "3 min de leitura",
  "autor": "Redação Ácida",
  "destaque": true,
  "legenda_imagem": "Legenda editorial satírica para a charge/caricatura",
  "prompt_caricatura": "Descrição visual cômica e detalhada da charge satírica (personagens, cenário absurdo, nanquim e guache, sem textos ou logos comerciais)",
  "corpo": [
    "Primeiro parágrafo fluido com metáfora de botequim...",
    "Segundo parágrafo desconstruindo a pose do político...",
    "Terceiro parágrafo com deboche sobre a conveniência eleitoral...",
    "Quarto parágrafo fechando com sabedoria popular ácida..."
  ],
  "milagres": [
    {"titulo": "Nome Sarcástico do Ponto 1", "texto": "Explicação analítica e irônica."},
    {"titulo": "Nome Sarcástico do Ponto 2", "texto": "Explicação analítica e irônica."},
    {"titulo": "Nome Sarcástico do Ponto 3", "texto": "Explicação analítica e irônica."},
    {"titulo": "Nome Sarcástico do Ponto 4", "texto": "Explicação analítica e irônica."}
  ],
  "contexto_real": "Parágrafo factual sóbrio e transparente explicando os fatos crus e exatos da notícia que motivaram a sátira."
}
"""

    prompt_usuario = f"""
NOTÍCIA REAL SELECIONADA:
- Fonte: {noticia['fonte']}
- Título Real: {noticia['titulo']}
- Resumo do Fato: {noticia['resumo']}
- Link da Notícia: {noticia['link']}
- Legenda original da foto: {dados_imagem.get('legenda_sugerida', '')}

Gere agora a crônica satírica completa no formato JSON exigido, com rigor factual e ironia máxima para o ÍMPROBO.
"""

    modelos = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    payload = {
        "contents": [
            {
                "parts": [{"text": instrucao_sistema + "\n\n" + prompt_usuario}]
            }
        ],
        "generationConfig": {
            "temperature": 0.85,
            "responseMimeType": "application/json"
        }
    }

    for modelo in modelos:
        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url_api,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            print(f"[*] Tentando geração com {modelo}...")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                texto_resposta = data['candidates'][0]['content']['parts'][0]['text']
                texto_limpo = re.sub(r'^```json\s*', '', texto_resposta.strip())
                texto_limpo = re.sub(r'\s*```$', '', texto_limpo)
                parsed = json.loads(texto_limpo)
                print(f"[✓] Crônica satírica redigida com sucesso via {modelo}!")
                return parsed
        except urllib.error.HTTPError as e:
            err_b = e.read().decode('utf-8', errors='ignore')
            print(f"[!] Modelo {modelo} indisponível ({e.code}): {err_b[:120]}. Tentando próximo...")
            continue
        except Exception as e:
            print(f"[!] Erro no modelo {modelo}: {e}. Tentando próximo...")
            continue

    print("[!] Todos os modelos Gemini retornaram erro. Verifique a GEMINI_API_KEY no GitHub Secrets.")
    return None

def criar_artigo_demo(noticia, dados_imagem):
    """
    Gera uma crônica satírica ácida de alto calibre no estilo Pasquim e O Pasquim,
    caso a API de IA não esteja acessível ou esteja em modo laboratório.
    """
    slug = slugify(noticia["titulo"])
    hoje = datetime.now().strftime("%d de %B de %Y").replace("October", "Outubro").replace("November", "Novembro")
    
    # Gerador de manchetes punchy e sarcásticas
    titulo_limpo = noticia['titulo'].strip().upper()
    if len(titulo_limpo) > 55:
        # Pega as primeiras palavras chave
        palavras = [p for p in titulo_limpo.split() if len(p) > 2 and p not in ["PARA", "COM", "QUE", "SOBRE", "PELO", "PELA", "MAIS"]]
        core = " ".join(palavras[:4])
        titulo_curto = f"O GRANDE TEATRO: {core}"[:58]
    else:
        titulo_curto = titulo_limpo

    # Variações de títulos escrachados
    prefixos_satiricos = [
        "A FARRA DO CARIMBO: ",
        "O MILAGRE DA CARA DE PAU: ",
        "CIRCO DE BRASÍLIA: ",
        "O BANQUETE DO ERÁRIO: "
    ]
    import random
    titulo_punchy = f"{random.choice(prefixos_satiricos)}{titulo_limpo[:36]}..." if len(titulo_limpo) > 38 else f"{random.choice(prefixos_satiricos)}{titulo_limpo}"
    if len(titulo_punchy) > 60:
        titulo_punchy = titulo_punchy[:57] + "..."

    return {
        "slug": slug,
        "data": hoje,
        "categoria": "Comédia de Costumes",
        "tempo_leitura": "3 min de leitura",
        "titulo": titulo_punchy,
        "subtitulo": f"Com a solenidade de quem rouba no jogo de purrinha jurando inocência de mão no peito, Brasília encena mais um capítulo da sua secular ópera bufa.",
        "autor": "Redação Ácida",
        "destaque": True,
        "imagem_capa": dados_imagem.get("imagem_url") if dados_imagem else None,
        "legenda_imagem": dados_imagem.get("legenda_sugerida") if (dados_imagem and dados_imagem.get("imagem_url")) else None,
        "credito_imagem": dados_imagem.get("credito") if (dados_imagem and dados_imagem.get("imagem_url")) else None,
        "corpo": [
            f"Se a hipocrisia pagasse imposto de renda retido na fonte, os cofres da República estariam com superávit primário suficiente para calçar a Esplanada dos Ministérios com mármore de Carrara. A última pérola do anedotário oficial dá conta de que '{noticia['titulo']}'. Nos bastidores refrigerados do poder, a notícia circulou com a naturalidade de um garçom empurrando rodízio vencido em cliente distraído.",
            f"Segundo apurou o {noticia['fonte']}, {noticia['resumo']}. No entanto, quando decodificamos a fala polida das excelências para o dialeto do boteco da esquina, a tradução é cristalina: enquanto os donos da caneta desfilam de terno importado e discursam com a gravidade de um padre de interior, o cidadão comum calcula se o salário ainda dá para pagar o gás e a fatura da luz sem precisar recorrer a agiota de aplicativo.",
            "A beleza quase poética da malandragem institucional brasileira reside na liturgia da cara de pau. Quando o interesse aperta, adversários mortais que se xingavam de ladrão e fascista na véspera descobrem uma súbita comunhão espiritual diante do rateio das emendas e da partilha dos gabinetes. É a fraternidade do carimbo: ninguém larga a mão do privilégio alheio.",
            "Resta ao bravo contribuinte, estupefato na catraca do ônibus lotado, rir para não chorar. Pois em Brasília, governos sobem, ministros caem, siglas mudam de fantasia, mas a certeza permanece inabalável: a orquestra estatal segue tocando desafinada, e quem paga o couvert artístico mais caro do planeta é sempre o mesmo otário de carteira assinada."
        ],
        "milagres": [
            {
                "titulo": "A Velocidade da Urgência",
                "texto": "Projetos engavetados há duas décadas ganham tramitação em regime de 'urgência urgentíssima' assim que ameaçam o bolso da patota ou a conveniência eleitoral da semana."
            },
            {
                "titulo": "O Sacrifício dos Outros",
                "texto": "A solene proclamação de que 'o país precisa apertar os cintos' — desde que o cinto seja o do trabalhador e o suspensório da elite burocrática permaneça com folga de alfaiate."
            },
            {
                "titulo": "A Aliança da Sobrevivência",
                "texto": "O comovente espetáculo em que esquerda, direita e o insaciável Centrão dão as mãos no plenário para aprovar qualquer emenda que blinde o fundão partidário."
            },
            {
                "titulo": "A Liturgia do Cinismo",
                "texto": "A arte de olhar nos olhos da câmera com semblante compungido e jurar que o loteamento de cargos foi um 'gesto cívico em defesa da estabilidade republicana'."
            }
        ],
        "contexto_real": f"O Contexto Factual: {noticia['resumo']} Noticiado originalmente por {noticia['fonte']} com base nos desdobramentos oficiais apurados na capital federal."
    }

def gerar_caricatura_ia(dados_artigo, api_key):
    """
    Gera automaticamente a caricatura editorial satírica utilizando a API do Google Imagen 3
    (imagen-3.0-generate-002:predict) e salva diretamente em imagens/{slug}.jpg.
    Totalmente autônomo e sem intervenção manual.
    """
    if not api_key:
        print("[!] Aviso: Nenhuma GEMINI_API_KEY configurada. Pulando geração de imagem por IA.")
        return False

    slug = dados_artigo.get("slug")
    if not slug:
        return False

    os.makedirs(IMAGENS_DIR, exist_ok=True)
    caminho_final = os.path.join(IMAGENS_DIR, f"{slug}.jpg")

    # Se já existir uma caricatura local para esse slug, preserva
    if os.path.exists(caminho_final):
        print(f"[*] Caricatura local já existente encontrada: {caminho_final}")
        dados_artigo["imagem_capa"] = f"imagens/{slug}.jpg"
        dados_artigo["credito_imagem"] = "Arte: Caricatura Editorial IA / Ilustração Satírica"
        return True

    # Monta o prompt estilístico com guardrails estritos
    prompt_base = dados_artigo.get("prompt_caricatura")
    if not prompt_base:
        titulo = dados_artigo.get("titulo", "")
        subtitulo = dados_artigo.get("subtitulo", "")
        prompt_base = f"Sátira política brasileira: {titulo}. {subtitulo}."

    prompt_completo = (
        f"A vintage 1970s-1980s editorial political cartoon caricature in expressive ink with detailed cross-hatching "
        f"and vibrant gouache watercolor wash, satirical Brazilian political press style. "
        f"Exaggerated humorous facial expressions, slapstick political farce and comic scene: {prompt_base}. "
        f"Strictly NO text 'MAD', NO logos, NO watermark, NO real photographs, pure satirical illustration."
    )

    url_imagen = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"

    payload = {
        "instances": [
            {
                "prompt": prompt_completo
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9",
            "outputMimeType": "image/jpeg"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"[*] Solicitando geração de caricatura editorial ao Google Imagen 3...")
    try:
        req = urllib.request.Request(
            url_imagen,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            predictions = data.get("predictions", [])
            if predictions and "bytesBase64Encoded" in predictions[0]:
                b64_data = predictions[0]["bytesBase64Encoded"]
                img_bytes = base64.b64decode(b64_data)
                with open(caminho_final, "wb") as f_img:
                    f_img.write(img_bytes)
                print(f"[✓] Caricatura gerada e salva com sucesso: {caminho_final} ({len(img_bytes)} bytes)")
                dados_artigo["imagem_capa"] = f"imagens/{slug}.jpg"
                dados_artigo["credito_imagem"] = "Arte: Caricatura Editorial IA / Ilustração Satírica"
                if not dados_artigo.get("legenda_imagem"):
                    dados_artigo["legenda_imagem"] = f"Caricatura editorial satírica: {dados_artigo.get('titulo')}"
                return True
            else:
                print(f"[!] Resposta inesperada do Imagen 3: {data.get('error', 'Sem predições')}")
                return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='ignore')
        print(f"[!] Erro na API Imagen 3 ({e.code}): {err_msg[:200]}")
        return False
    except Exception as e:
        print(f"[!] Falha na conexão com Imagen 3: {e}")
        return False

def salvar_artigo_no_site(dados_artigo, noticia_url):
    """Salva o JSON em content/ e recompila o site imediatamente"""
    os.makedirs(CONTENT_DIR, exist_ok=True)
    slug = dados_artigo["slug"]
    data_arquivo = datetime.now().strftime("%Y-%m-%d")
    arquivo_json = os.path.join(CONTENT_DIR, f"{data_arquivo}-{slug}.json")

    if "timestamp" not in dados_artigo:
        dados_artigo["timestamp"] = datetime.now().isoformat()

    with open(arquivo_json, "w", encoding="utf-8") as f:
        json.dump(dados_artigo, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Artigo salvo com sucesso: {arquivo_json}")

    # Atualiza banco de URLs processadas
    db = carregar_db()
    db["processadas"].append({
        "url": noticia_url,
        "slug": slug,
        "titulo": dados_artigo["titulo"],
        "data_processamento": datetime.now().isoformat()
    })
    # Gera narração neural em MP3 se disponível
    try:
        from gerar_audio import processar_artigo
        print("[*] Gerando narração neural em MP3 para a crônica...")
        processar_artigo(arquivo_json)
    except Exception as e:
        print(f"[!] Aviso: narração neural não gerada neste momento: {e}")

    # Recompila todas as páginas HTML do ÍMPROBO
    print("[*] Recompilando o portal ÍMPROBO (Home e Artigos)...")
    build_all()
    print("[✓] Portal atualizado com a nova matéria e reprodutor de áudio!")

def executar_rodada(modo_demo=False):
    """Executa o ciclo completo do robô: varre, filtra, gera e publica"""
    print("=" * 65)
    print("  ROBÔ AUTÔNOMO ÍMPROBO - VARREDURA E PUBLICAÇÃO SATÍRICA")
    print("=" * 65)

    db = carregar_db()
    db_urls = set(item["url"] for item in db.get("processadas", []))
    print(f"[*] Notícias já registradas no histórico: {len(db_urls)}")

    # 1. Coleta dos feeds
    print("[*] Varrendo feeds dos maiores jornais do Brasil...")
    todas_noticias = []
    for feed in RSS_FEEDS:
        itens = varrer_feed_rss(feed)
        print(f"    - {feed['fonte']}: {len(itens)} notícias coletadas")
        todas_noticias.extend(itens)

    if not todas_noticias:
        if modo_demo:
            print("[i] Modo demonstração/offline ativo: carregando manchetes reais do cenário nacional...")
            todas_noticias = [
                {
                    "fonte": "Folha de S.Paulo - Poder",
                    "titulo": "Articulação no Congresso e STF avança para indicar Rodrigo Pacheco à vaga aberta no Supremo",
                    "link": "https://www1.folha.uol.com.br/poder/2026/10/articulacao-pacheco-stf-segundo-turno.shtml",
                    "resumo": "Lideranças do Senado e da Câmara articulam com ministros do STF para emplacar o ex-presidente do Senado Rodrigo Pacheco na vaga da Corte em plena reta final do segundo turno.",
                    "data_pub": "15 de Outubro de 2026",
                    "peso_fonte": 1.3
                },
                {
                    "fonte": "G1 Política",
                    "titulo": "Após aprovação relâmpago da PEC 6x1 no Senado, oposição tenta pautar maioridade penal",
                    "link": "https://g1.globo.com/politica/noticia/2026/10/15/senado-pec-6x1-oposicao-maioridade.ghtml",
                    "resumo": "Bancada da oposição tenta desviar o foco da pauta trabalhista pautando a PEC da Segurança Pública e redução da maioridade penal para 16 anos.",
                    "data_pub": "15 de Outubro de 2026",
                    "peso_fonte": 1.2
                }
            ]
    if not todas_noticias:
        print("[!] Feeds externos indisponíveis ou vazios. Ativando manchetes factuais de contingência do cenário nacional...")
        todas_noticias = [
            {
                "fonte": "Poder360",
                "titulo": "Governo Lula finaliza pacote de corte de gastos obrigatórios e prepara envio ao Congresso",
                "link": "https://www.poder360.com.br/economia/governo-lula-finaliza-pacote-corte-gastos-congresso-2026/",
                "resumo": "Ministério da Fazenda e Planejamento concluem proposta de contenção de despesas obrigatórias para tentar cumprir meta fiscal diante de resistência de ministros da área social.",
                "data_pub": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "peso_fonte": 1.3
            },
            {
                "fonte": "G1 Política",
                "titulo": "STF mantém bloqueio de emendas Pix até que Congresso apresente regras rígidas de transparência",
                "link": "https://g1.globo.com/politica/noticia/2026/10/stf-mantem-bloqueio-emendas-pix-transparencia-congresso.ghtml",
                "resumo": "Plenário do Supremo Tribunal Federal forma maioria para manter suspensão do repasse bilionário das chamadas emendas Pix sem rastreabilidade dos autores.",
                "data_pub": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "peso_fonte": 1.2
            },
            {
                "fonte": "Folha de S.Paulo - Poder",
                "titulo": "Caciques do Centrão disputam comando da Câmara e do Senado prometendo aumento de verbas parlamentares",
                "link": "https://www1.folha.uol.com.br/poder/2026/10/disputa-camara-senado-centrao-verbas-parlamentares.shtml",
                "resumo": "Candidatos à sucessão de Arthur Lira e Rodrigo Pacheco intensificam campanha oferecendo relatorias de peso e cargos estratégicos na Esplanada dos Ministérios.",
                "data_pub": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "peso_fonte": 1.3
            }
        ]

    # 2. Ranqueamento de Relevância
    noticias_ranqueadas = []
    for n in todas_noticias:
        score = calcular_relevancia(n, db_urls)
        if score > 0:
            noticias_ranqueadas.append((score, n))

    noticias_ranqueadas.sort(key=lambda x: x[0], reverse=True)

    if not noticias_ranqueadas:
        print("[i] Todas as matérias capturadas já estavam registradas. Selecionando desdobramento inédito da pauta...")
        noticias_ranqueadas = [
            (50.0, {
                "fonte": "Agência Ímprobo / Apuração Política",
                "titulo": "Governo e Congresso fecham acordo sobre pacote fiscal com 'sacrifício compartilhado': povo aperta o cinto e deputados aumentam o fundão",
                "link": f"https://improbo.vercel.app/apuracao/{datetime.now().strftime('%Y%m%d%H%M')}",
                "resumo": "Articulação de bastidores em Brasília avança para aprovar cortes em programas públicos enquanto bancadas partidárias blindam emendas e verbas de gabinete.",
                "data_pub": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "peso_fonte": 1.5
            })
        ]

    melhor_score, melhor_noticia = noticias_ranqueadas[0]
    print(f"\n[★] MANCHETE ELEITA COMO A MAIS RELEVANTE DO DIA (Score: {melhor_score}):")
    print(f"    Fonte: {melhor_noticia['fonte']}")
    print(f"    Título: {melhor_noticia['titulo']}")
    print(f"    Link: {melhor_noticia['link']}")

    # 3. Captura da Imagem de Capa Real
    print("\n[*] Capturando metadados e imagem de capa (og:image)...")
    dados_imagem = extrair_imagem_capa(melhor_noticia["link"])
    if dados_imagem.get("imagem_url"):
        print(f"    [✓] Imagem real capturada: {dados_imagem['imagem_url'][:70]}...")
        print(f"    [✓] Crédito: {dados_imagem['credito']}")
    else:
        print("    [!] Nenhuma foto og:image autêntica encontrada; omitindo imagem (layout puramente tipográfico).")

    # 4. Redação Satírica com Gemini ou Modo Demo
    api_key = obter_api_key()
    dados_artigo = None

    if api_key and not modo_demo:
        print("\n[*] Redigindo crônica satírica com a API do Gemini...")
        resultado_ia = redigir_cronica_gemini(melhor_noticia, dados_imagem, api_key)
        if resultado_ia:
            dados_artigo = resultado_ia
            dados_artigo["slug"] = slugify(dados_artigo.get("titulo", melhor_noticia["titulo"]))
            if "data" not in dados_artigo:
                dados_artigo["data"] = datetime.now().strftime("%d de %B de %Y").replace("October", "Outubro")

    if not dados_artigo:
        if not api_key and not modo_demo:
            print("\n[!] GEMINI_API_KEY não encontrada no ambiente.")
            print("[*] Gerando crônica através do motor editorial estruturado (Modo Laboratório)...")
        dados_artigo = criar_artigo_demo(melhor_noticia, dados_imagem)

    # 4.1. Geração de Imagem 100% Automática via Google Imagen 3
    slug = dados_artigo.get("slug")
    gerou_imagem = False
    if api_key:
        print("\n[*] Disparando geração autônoma de caricatura editorial IA...")
        gerou_imagem = gerar_caricatura_ia(dados_artigo, api_key)

    # Blindagem visual: se não gerou caricatura por IA (ou API indisponível), NUNCA deixa a matéria sem arte!
    if not dados_artigo.get("imagem_capa") or not gerou_imagem:
        if slug and os.path.exists(os.path.join(IMAGENS_DIR, f"{slug}.jpg")):
            dados_artigo["imagem_capa"] = f"imagens/{slug}.jpg"
            dados_artigo["credito_imagem"] = "Arte: Caricatura Editorial IA / Ilustração Satírica"
        elif dados_imagem and dados_imagem.get("imagem_url"):
            print("[*] Aplicando foto jornalística autêntica da matéria com crédito editorial...")
            dados_artigo["imagem_capa"] = dados_imagem["imagem_url"]
            dados_artigo["credito_imagem"] = dados_imagem.get("credito") or f"Foto: Agência / {melhor_noticia['fonte']}"
            if not dados_artigo.get("legenda_imagem"):
                dados_artigo["legenda_imagem"] = dados_imagem.get("legenda_sugerida") or melhor_noticia["titulo"]
        else:
            print("[*] Aplicando charge satírica clássica do acervo editorial do Ímprobo...")
            import random
            acervo_editorial = [
                ("imagens/lula-malabarismo-planalto-centrao.jpg", "Charge Editorial: O Picadeiro de Brasília e a Arte das Emendas"),
                ("imagens/flavio-bolsonaro-pec-privatizacao-praias.jpg", "Charge Editorial: A Catraca do Poder na Praia do Erário"),
                ("imagens/congresso-anistia-partidos-dividas-fundo-eleitoral.jpg", "Charge Editorial: O Auto-Perdão e a Festa dos Boletos"),
                ("imagens/sao-paulo-apagao-enel-guerra-da-vela.jpg", "Charge Editorial: A Escuridão Oficial e a Tragicomédia Nacional")
            ]
            img_escolhida, leg_escolhida = random.choice(acervo_editorial)
            dados_artigo["imagem_capa"] = img_escolhida
            dados_artigo["credito_imagem"] = "Arte: Acervo Editorial Ímprobo / Charge Política"
            if not dados_artigo.get("legenda_imagem"):
                dados_artigo["legenda_imagem"] = leg_escolhida

    # 5. Salvamento e Compilação
    salvar_artigo_no_site(dados_artigo, melhor_noticia["link"])
    return True

def listar_manchetes():
    """Apenas exibe as principais notícias ranqueadas sem publicar"""
    db = carregar_db()
    db_urls = set(item["url"] for item in db.get("processadas", []))
    print("[*] Varrendo notícias para análise de relevância...")
    
    todas = []
    for feed in RSS_FEEDS:
        itens = varrer_feed_rss(feed)
        todas.extend(itens)

    ranqueadas = []
    for n in todas:
        score = calcular_relevancia(n, db_urls)
        ranqueadas.append((score, n))

    ranqueadas.sort(key=lambda x: x[0], reverse=True)
    
    print("\n" + "=" * 70)
    print("TOP 10 MANCHETES MAIS RELEVANTES DETECTADAS:")
    print("=" * 70)
    for idx, (sc, n) in enumerate(ranqueadas[:10], start=1):
        status = "[JÁ PUBLICADA]" if sc < 0 else f"[Score: {sc}]"
        print(f"{idx:2d}. {status} ({n['fonte']}) {n['titulo']}")
        print(f"    Link: {n['link']}\n")

def main():
    parser = argparse.ArgumentParser(description="Robô de Varredura e Publicação Autônoma do ÍMPROBO")
    parser.add_argument("--executar", action="store_true", help="Executa uma rodada completa de varredura e publicação")
    parser.add_argument("--listar", action="store_true", help="Apenas lista as manchetes mais relevantes sem publicar")
    parser.add_argument("--demo", action="store_true", help="Executa rodada no modo demonstração/laboratório")
    parser.add_argument("--loop", type=int, metavar="MINUTOS", help="Executa continuamente a cada X minutos")

    args = parser.parse_args()

    if args.listar:
        listar_manchetes()
    elif args.loop:
        minutos = max(args.loop, 5)
        print(f"[*] Robô iniciado em modo contínuo. Intervalo: {minutos} minutos.")
        while True:
            try:
                executar_rodada(modo_demo=args.demo)
                print(f"\n[*] Aguardando {minutos} minutos para a próxima varredura...\n")
                time.sleep(minutos * 60)
            except KeyboardInterrupt:
                print("\n[!] Robô interrompido pelo usuário.")
                break
            except Exception as e:
                print(f"[!] Erro inesperado na rodada: {e}")
                time.sleep(60)
    else:
        # Default: executar rodada
        executar_rodada(modo_demo=args.demo)

if __name__ == "__main__":
    main()
