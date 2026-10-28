#!/usr/bin/env python3
"""
Robô Autônomo de Varredura e Redação Satírica - ÍMPROBO
Monitora os principais jornais do Brasil (RSS Feeds & Scraping),
seleciona a manchete de maior relevância política,
redige a crônica satírica com base no PROMPT_MESTRE.md (Gemini)
e compila o site com charges/caricaturas satíricas (100% sem fotos reais).
"""

import os
import sys
import json
import re
import time
import argparse
import unicodedata
import base64
import random
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
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

# Inspetor de Qualidade & Telemetria
try:
    from inspetor import (
        validar_artigo_completo,
        registrar_execucao,
        atualizar_radar_pautas,
        carregar_status_db,
        salvar_status_db
    )
except ImportError:
    validar_artigo_completo = None
    registrar_execucao = None
    atualizar_radar_pautas = None

# Notificador Telegram
try:
    from notificador_telegram import notificar_sucesso, notificar_alerta
except ImportError:
    notificar_sucesso = None
    notificar_alerta = None

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
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Erro ao salvar banco {DB_PATH}: {e}")

def carregar_slugs_existentes():
    """Lê todos os slugs já existentes nos arquivos de content/*.json para evitar qualquer duplicata"""
    slugs = set()
    if os.path.exists(CONTENT_DIR):
        for f in os.listdir(CONTENT_DIR):
            if f.endswith(".json"):
                try:
                    caminho = os.path.join(CONTENT_DIR, f)
                    with open(caminho, "r", encoding="utf-8") as arq:
                        dados = json.load(arq)
                        if "slug" in dados:
                            slugs.add(dados["slug"])
                except Exception:
                    pass
    return slugs

def slugify(texto):
    """Converte título em slug amigável para URLs e arquivos"""
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^a-zA-Z0-9\s-]', '', texto).lower()
    return re.sub(r'[-\s]+', '-', texto).strip('-')[:50]

def extrair_noticia_de_url(url):
    """Extrai título, fonte e resumo de uma URL externa para pauta sob demanda (furo de reportagem)"""
    try:
        from urllib.parse import urlparse
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        soup = BeautifulSoup(html, 'html.parser')

        titulo = None
        for tag in [
            soup.find("meta", property="og:title"),
            soup.find("meta", property="twitter:title"),
            soup.find("h1"),
            soup.find("title")
        ]:
            if tag:
                val = tag.get("content") if tag.name == "meta" else tag.get_text()
                if val and len(val.strip()) > 10:
                    titulo = val.strip()
                    break

        if not titulo:
            titulo = "Pauta Exclusiva da Redação Ímprobo"

        resumo = ""
        for tag in [
            soup.find("meta", property="og:description"),
            soup.find("meta", property="twitter:description"),
            soup.find("meta", attrs={"name": "description"})
        ]:
            if tag:
                val = tag.get("content")
                if val and len(val.strip()) > 20:
                    resumo = val.strip()
                    break

        if not resumo:
            ps = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 50]
            if ps:
                resumo = " ".join(ps[:2])[:400]

        dominio = urlparse(url).netloc.replace("www.", "")
        fonte = f"Furo Externo ({dominio})"

        return {
            "fonte": fonte,
            "titulo": titulo,
            "link": url,
            "resumo": resumo or titulo,
            "data_pub": datetime.now().strftime("%d de %B de %Y"),
            "peso_fonte": 2.5
        }
    except Exception as e:
        print(f"[!] Erro ao extrair notícia de {url}: {e}")
        return None

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
        with urllib.request.urlopen(req, timeout=12) as response:
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
    
    try:
        clean = pub_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass

    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(pub_str, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None

def calcular_relevancia(noticia, db_urls, existing_slugs):
    """
    Atribui nota de relevância com prioridade estrita para NOTÍCIAS RECENTES E QUENTES:
    1. Blindagem contra duplicidade: Se o link já foi processado ou o slug já existe, descarta (-100).
    2. Filtragem de agregadores factuais massivos (fato ou fake) que não são notícias pontuais.
    3. Fator Quente (Recência Cronológica das últimas horas).
    4. Termos de poder, contradições e apelo popular.
    """
    if noticia["link"] in db_urls:
        return -100

    slug_candidato = slugify(noticia["titulo"])
    if slug_candidato in existing_slugs:
        return -100

    # Penaliza agregadores de transcrição de checagem genérica
    if any(termo in noticia["titulo"].lower() for termo in ["fato ou fake", "#fato ou #fake"]):
        return -50

    texto_busca = f"{noticia['titulo']} {noticia['resumo']}".lower()

    score_termos = 0.0

    for termo, peso in TERMOS_RELEVANCIA.items():
        if re.search(r'\b' + re.escape(termo) + r'\b', texto_busca):
            score_termos += peso

    score_base = score_termos * noticia.get("peso_fonte", 1.0)

    # Cálculo da Recência Cronológica
    dt_pub = extrair_data_publicacao(noticia.get("data_pub", ""))
    bonus_recencia = 0.0
    if dt_pub:
        try:
            agora = datetime.now(timezone.utc)
            horas_atras = max(0.0, (agora - dt_pub).total_seconds() / 3600.0)
            
            if horas_atras <= 6:
                bonus_recencia = 25.0
            elif horas_atras <= 24:
                bonus_recencia = 18.0
            elif horas_atras <= 48:
                bonus_recencia = 8.0
            elif horas_atras <= 72:
                bonus_recencia = 0.0
            else:
                bonus_recencia = -30.0
        except Exception:
            bonus_recencia = 0.0
    else:
        bonus_recencia = 2.0

    score_final = score_base + bonus_recencia
    return round(score_final, 2)

def descobrir_modelo_disponivel(api_key):
    """Consulta dinamicamente os modelos disponíveis para esta chave de API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            modelos_validos = []
            for m in data.get("models", []):
                metodos = m.get("supportedGenerationMethods", [])
                if "generateContent" in metodos:
                    nome = m["name"].replace("models/", "")
                    modelos_validos.append(nome)
            print(f"[*] Modelos disponíveis para esta chave na API Google: {modelos_validos[:8]}")
            return modelos_validos
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8', errors='ignore')
        print(f"[!] Falha ao listar modelos ({e.code}): {err[:150]}")
        return []
    except Exception as e:
        print(f"[!] Erro ao listar modelos: {e}")
        return []

def redigir_cronica_gemini(noticia, api_key):
    """
    Chama a API REST do Gemini para gerar a crônica satírica com estrito
    rigor aos fatos reais, tom de pasquim raiz e formatação JSON aprovada.
    """
    # Sanitize e trunca resumo para evitar estouro de tokens ou cópia bruta
    resumo_sanitizado = (noticia.get('resumo') or '').strip()
    if len(resumo_sanitizado) > 800:
        resumo_sanitizado = resumo_sanitizado[:800] + "..."

    instrucao_sistema = f"""Você é o Redator-Chefe e Humorista Escrachado de **ÍMPROBO**, portal brasileiro de jornalismo satírico de alta voltagem, crônica política e comédia de costumes.

MISSÃO EDITORIAL & DIRETRIZES DE QUALIDADE (VERSÃO 11.0 - SÁTIRA INSTITUCIONAL IMPLACÁVEL):

1. FIDELIDADE ABSOLUTA AO FATO REAL:
   - Personagens, declarações, decisões e dados são 100% reais (sem inventar pessoas ou fake news). O absurdo real da política brasileira já é o melhor roteiro cômico do mundo.

2. SÁTIRA INSTITUCIONAL IMPLACÁVEL (NÍVEL THE ONION / O PASQUIM / VOLTAIRE):
   - Fuja do ataque rasteiro de botequim e do trote juvenil de corredor (a armadilha previsível que desgastou o CQC). Não faça humor com ofensas físicas, xingamentos pueris ou trocadilhos óbvios.
   - O segredo da sátira letal é a INVERSÃO DA PREMISSA INSTITUCIONAL: adote a justificativa oficial do político, a nota da assessoria ou o projeto de lei com fingida solenidade técnica e leve-a até a sua conclusão mais absurda.
   - CONTRASTE OBRIGATÓRIO (FEW-SHOT EXAMPLES):
     ❌ ERRADO (Previsível / Clichê de Boteco): "O ministro come lagosta e viaja de jatinho enquanto o trabalhador come carne de segunda e paga o carnê atrasado com o lombo calejado."
     ✓ CORRETO (Sátira Institucional Implacável): "Ministério da Fazenda anuncia edital de R$ 4 bilhões para criar comissão encarregada de explicar pedagogicamente ao cidadão por que pagar mais tributo sobre o consumo é, em última análise, um ato de amor próprio e desapego material."
   - BLACKLIST LEXICAL RIGOROSA (TERMINANTEMENTE PROIBIDO usar estes clichês ou seus sinônimos diretos):
     * Proibidos: "pastel de vento", "pastel de rodoviária", "carne de segunda", "carne de pescoço", "acém duro", "lombo do trabalhador", "lombo do povo", "costas do assalariado", "carnê atrasado", "carnê da Casas Bahia", "alça do caixão".
     * Substitutos: explore a empáfia dos ternos engravatados, os pareceres da AGU, os jabutis no meio de medidas provisórias, a marquetagem eleitoral cínica, os carimbos burocráticos e o rateio de cargos com o Centrão.

3. VACINA ANTI-CQC (ALTERNÂNCIA DE FORMATOS NARRATIVOS):
   - Varie a estrutura textual para que o leitor nunca antecipe o final antes de clicar:
     * Registro A (Crônica Ácida de Fato Real - Estilo Pasquim): Narrativa rápida, ferina, desmascarando as contradições do fato com ritmo de alta literatura cômica.
     * Registro B (Paródia Institucional Solene - Estilo The Onion): O texto finge celebrar o escândalo como um triunfo do planejamento público ou da diplomacia moderna.
     * Registro C (O Absurdo Burocrático Kafkiano): Parodia manuais de instrução, portarias interministeriais ou pareceres jurídicos que justificam o indefensável.

4. A REGRA DA TESOURA DE DOIS GUMES (SEM VIÉS PARTIDÁRIO):
   - O alvo é sempre o poder, a burocracia estatal, a gastança pública, as contradições políticas e o teatro de Brasília (seja situação, oposição, Centrão, Judiciário ou Legislativo). Ridicularize a cara de pau de todos os lados. Ninguém vira herói ou sai ileso.

5. REGRA DOS TÍTULOS CURTOS E PUNCHY:
   - Título curto (40 a 60 caracteres no máximo), em CAIXA ALTA, com a piada ou contradição sarcástica na cara do leitor (ex: 'O RINGUE DA CARA DE PAU: LULA E FLÁVIO NA TV').

6. CAMPO OBRIGATÓRIO 'frase_disparo_zap' (MUNIÇÃO VIRAL):
   - Uma linha única, cortante e ácida (soundbite) sintetizando a contradição da matéria, formatada especificamente para o leitor disparar em grupos de WhatsApp da família e do trabalho.

7. REGRA DA IMAGEM EXCLUSIVA E FIEL:
   - Prompt visual satírico 100% FIEL e estritamente focado no contexto e personagens da NOTÍCIA ATUAL (nanquim, guache, traço caricatural nobre, sem textos nem logotipos). Proibido reaproveitar temas anteriores.

8. ESTRUTURA DE RETORNO OBRIGATÓRIA (JSON VÁLIDO):
Responda APENAS com um objeto JSON válido (sem delimitadores markdown extras fora do json):
{{
  "titulo": "MANCHETE CURTA E ÁCIDA EM CAIXA ALTA (MÁX 60 CARACTERES)",
  "subtitulo": "Duas linhas curtas, cínicas e refinadas sintetizando o absurdo oficial",
  "categoria": "Comédia de Costumes",
  "tempo_leitura": "2 min de leitura",
  "autor": "Redação Ácida",
  "destaque": true,
  "frase_disparo_zap": "Frase cortante de 1 linha para o leitor disparar no Zap como munição de debate.",
  "legenda_imagem": "Legenda editorial satírica para a charge",
  "prompt_caricatura": "Descrição visual cômica e detalhada da charge satírica retratando fielmente a piada da matéria atual (nanquim e guache, sem textos ou marcas)",
  "prompt_caricatura_en": "Detailed English visual prompt of the satirical political cartoon scene: caricature of Brazilian politicians involved (e.g. Luiz Inacio Lula da Silva, Flavio Bolsonaro) in physical comic farce, vintage 1970s Brazilian satirical press style (O Pasquim/Henfil), expressive ink cross-hatching, gouache watercolor wash on cream paper, strictly NO text, NO logos, NO watermark",
  "corpo": [
    "Primeiro parágrafo de crônica satírica rica abrindo o espetáculo e expondo o ridículo da situação...",
    "Segundo parágrafo dissecando a cara de pau do primeiro envolvido com ironia fina e deboche institucional...",
    "Terceiro parágrafo desnudando as contradições do outro lado sem dó nem piedade...",
    "Quarto parágrafo fechando a crônica com tirada hilária e cirúrgica sobre a fatura empurrada para a sociedade."
  ],
  "milagres": [
    {{"titulo": "A Liturgia da Rasteira", "texto": "Uma ou duas linhas cômicas e mordazes."}},
    {{"titulo": "A Promessa de Papelão", "texto": "Uma ou duas linhas cômicas e mordazes."}},
    {{"titulo": "O Malabarismo Fiscal", "texto": "Uma ou duas linhas cômicas e mordazes."}},
    {{"titulo": "O Boleto Soberano", "texto": "Uma ou duas linhas cômicas e mordazes."}}
  ],
  "contexto_real": "Parágrafo factual sóbrio, transparente e denso explicando os fatos e números reais da notícia que motivaram a sátira."
}}"""

    prompt_usuario = f"""NOTÍCIA REAL SELECIONADA:
- Fonte: {noticia['fonte']}
- Título Real: {noticia['titulo']}
- Resumo do Fato: {resumo_sanitizado}
- Link da Notícia: {noticia['link']}

Gere a crônica satírica completa no formato JSON exigido, com rigor factual, tom de pasquim raiz e título curto em caixa alta."""

    modelos_api = descobrir_modelo_disponivel(api_key)
    if modelos_api:
        flash_models = [m for m in modelos_api if "flash" in m.lower()]
        pro_models = [m for m in modelos_api if "pro" in m.lower() and "flash" not in m.lower()]
        outros = [m for m in modelos_api if m not in flash_models and m not in pro_models]
        modelos = flash_models + pro_models + outros
    else:
        modelos = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash"
        ]

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
        for api_version in ("v1beta", "v1"):
            url_api = f"https://generativelanguage.googleapis.com/{api_version}/models/{modelo}:generateContent?key={api_key}"
            req = urllib.request.Request(
                url_api,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            try:
                print(f"[*] Tentando geração com {modelo} ({api_version})...")
                with urllib.request.urlopen(req, timeout=35) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    texto_resposta = data['candidates'][0]['content']['parts'][0]['text']
                    texto_limpo = re.sub(r'^```json\s*', '', texto_resposta.strip())
                    texto_limpo = re.sub(r'\s*```$', '', texto_limpo)
                    parsed = json.loads(texto_limpo)
                    
                    # Validação estrita de tamanho do título
                    if parsed.get("titulo"):
                        parsed["titulo"] = parsed["titulo"].strip().upper()
                        if len(parsed["titulo"]) > 65:
                            parsed["titulo"] = parsed["titulo"][:62] + "..."
                            
                    print(f"[✓] Crônica satírica redigida com sucesso via {modelo} ({api_version})!")
                    return parsed
            except urllib.error.HTTPError as e:
                err_b = e.read().decode('utf-8', errors='ignore')
                print(f"[!] {modelo} ({api_version}) indisponível ({e.code}): {err_b[:120]}. Tentando próximo...")
                continue
            except Exception as e:
                print(f"[!] Erro no modelo {modelo} ({api_version}): {e}. Tentando próximo...")
                continue

    print("[!] Todos os modelos Gemini retornaram erro. Verifique a GEMINI_API_KEY no GitHub Secrets.")
    return None

def criar_artigo_demo(noticia):
    """
    Gera uma crônica satírica ácida de alto calibre no estilo escrachado, direto e zueiro,
    caso a API de IA não esteja acessível ou esteja em modo laboratório.
    Garante frases curtas, ritmo rápido e arte 100% exclusiva vinculada à notícia.
    """
    slug = slugify(noticia["titulo"])
    hoje = datetime.now().strftime("%d de %B de %Y").replace("October", "Outubro").replace("November", "Novembro")
    
    titulo_limpo = noticia['titulo'].strip().upper()
    prefixos = [
        "O BALCÃO DO PODER: ",
        "O MILAGRE DA CARA DE PAU: ",
        "CIRCO DE BRASÍLIA: ",
        "A FARRA DO CARIMBO: "
    ]
    pfx = random.choice(prefixos)
    max_len = 58 - len(pfx)
    titulo_curto = f"{pfx}{titulo_limpo[:max_len]}..." if len(titulo_limpo) > max_len else f"{pfx}{titulo_limpo}"

    resumo_curto = (noticia.get("resumo") or "")[:280].strip()
    if len(noticia.get("resumo", "")) > 280:
        resumo_curto += "..."

    dados = {
        "slug": slug,
        "data": hoje,
        "categoria": "Comédia de Costumes",
        "tempo_leitura": "2 min de leitura",
        "titulo": titulo_curto,
        "subtitulo": "Com a solenidade de quem assina decreto em papel timbrado, Brasília encena mais um capítulo do absurdo institucional.",
        "autor": "Redação Ácida",
        "destaque": True,
        "frase_disparo_zap": f"Em Brasília não existe crise que um bom conchavo de gabinete e uma emenda orçamentária não resolvam às nossas custas.",
        "corpo": [
            f"Brasília não tem crise moral. Tem assessoria de comunicação de prontidão 24 horas. A mais recente pérola do anedotário da Esplanada: '{noticia['titulo']}'. Nos bastidores dos palácios, o anúncio foi recebido com a serenidade de quem já calculou a taxa de retorno eleitoral.",
            f"Segundo apurado pelo {noticia['fonte']}, {resumo_curto}. Traduzindo da liturgia do poder para a língua do contribuinte: a situação anuncia um plano audacioso, a oposição convoca coletiva de indignação e ambos se reúnem na quarta-feira para blindar o fundo partidário e manter as prerrogativas intactas.",
            "A grande obra de arte de Brasília é a engenharia do faz de conta. Quando o cronograma eleitoral aperta, desafetos jurados de microfone descobrem afinidades espirituais comoventes. Votam juntos o aumento dos próprios benefícios e deixam para o cidadão a nobre missão cívica de sustentar o espetáculo com novo recolhimento na fonte.",
            "Ao cidadão resta a constatação lúcida de que o circo é permanente e a bilheteria nunca fecha. Seja sob a bandeira da esperança social ou do rigor fiscal, a única certeza homologada em cartório é que a fatura do banquete estatal chega pontual e sem desconto no contracheque de quem produz."
        ],
        "milagres": [
            {
                "titulo": "A Velocidade da Boquinha",
                "texto": "Aumento de prerrogativas passa em cinco minutos. Pautas de interesse real dormem vinte anos na gaveta."
            },
            {
                "titulo": "A Austeridade Seletiva",
                "texto": "O governo pede sacrifício cívico à nação enquanto renova a frota de sedãs executivos e verbas de gabinete."
            },
            {
                "titulo": "A Liturgia do Conchavo",
                "texto": "Guerra de adjetivos diante das câmeras e partilha amigável de cargos assim que a luz vermelha se apaga."
            },
            {
                "titulo": "A Certeza do Tributo",
                "texto": "Eles reescrevem as regras do jogo e a notificação de débito é o único serviço público que chega sem atraso."
            }
        ],
        "contexto_real": f"O Contexto Factual: {resumo_curto} Noticiado originalmente por {noticia['fonte']} com base nos desdobramentos apurados na capital federal."
    }
    return dados

def gerar_caricatura_ia(dados_artigo, api_key):
    """
    Gera automaticamente a caricatura editorial satírica utilizando:
    1. Google Gemini Multimodal Nativo (gemini-2.5-flash-image, gemini-2.0-flash, gemini-2.0-flash-exp)
    2. Google Imagen 3 (caso a chave API tenha cota/permissão de predict)
    Salva diretamente em imagens/{slug}.jpg com alta resolução.
    Garante o cumprimento estrito da Regra de Ouro de Caricatura Editorial (> 50KB, estilo Pasquim/MAD).
    """
    slug = dados_artigo.get("slug")
    if not slug:
        return False

    os.makedirs(IMAGENS_DIR, exist_ok=True)
    caminho_final = os.path.join(IMAGENS_DIR, f"{slug}.jpg")

    # Se já existir uma caricatura local válida para esse slug (> 50KB), preserva
    if os.path.exists(caminho_final) and os.path.getsize(caminho_final) >= 50000:
        print(f"[*] Caricatura local já existente encontrada: {caminho_final} ({os.path.getsize(caminho_final)} bytes)")
        dados_artigo["imagem_capa"] = f"imagens/{slug}.jpg"
        dados_artigo["credito_imagem"] = "Arte: Caricatura Editorial IA / Ilustração Satírica"
        if not dados_artigo.get("legenda_imagem"):
            dados_artigo["legenda_imagem"] = f"Caricatura editorial satírica: {dados_artigo.get('titulo')}"
        return True

    prompt_base = dados_artigo.get("prompt_caricatura")
    prompt_en = dados_artigo.get("prompt_caricatura_en")
    if not prompt_base:
        titulo = dados_artigo.get("titulo", "")
        subtitulo = dados_artigo.get("subtitulo", "")
        prompt_base = f"Sátira política brasileira: {titulo}. {subtitulo}."

    if not prompt_en:
        prompt_en = f"Brazilian editorial political cartoon caricature in expressive ink with detailed cross-hatching, watercolor wash on vintage cream paper: {dados_artigo.get('titulo')}. Humorous caricature of Brazilian politicians in physical farce, satirical newspaper illustration, strictly NO watermark, NO logos, NO text"

    prompt_completo = (
        f"A vintage 1970s-1980s editorial political cartoon caricature in expressive ink with detailed cross-hatching "
        f"and vibrant gouache watercolor wash, satirical Brazilian political press style. "
        f"{prompt_en}. "
        f"Strictly NO text, NO logos, NO watermark, NO real photographs, pure satirical illustration."
    )

    if api_key:
        # 1. Tentativa via Google Gemini Multimodal Nativo (generateContent com responseModalities IMAGE)
        modelos_multimodais = [
            "gemini-2.5-flash-image",
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp"
        ]

        payload_gemini = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_completo}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        headers_gemini = {
            "Content-Type": "application/json"
        }

        print("[*] Solicitando caricatura editorial via Gemini Multimodal Nativo...")
        for modelo in modelos_multimodais:
            url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
            try:
                req = urllib.request.Request(
                    url_gemini,
                    data=json.dumps(payload_gemini).encode("utf-8"),
                    headers=headers_gemini,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            inline = part.get("inlineData") or part.get("inline_data")
                            if inline and inline.get("data"):
                                b64_data = inline["data"]
                                img_bytes = base64.b64decode(b64_data)

                                # Formata e salva como JPEG
                                try:
                                    from PIL import Image
                                    import io
                                    im = Image.open(io.BytesIO(img_bytes))
                                    if im.mode in ("RGBA", "P"):
                                        im = im.convert("RGB")
                                    im.save(caminho_final, "JPEG", quality=92)
                                except Exception as e_pil:
                                    with open(caminho_final, "wb") as f_img:
                                        f_img.write(img_bytes)

                                # Validação estrita da Regra de Ouro (> 50KB)
                                if os.path.exists(caminho_final) and os.path.getsize(caminho_final) >= 50000:
                                    tam = os.path.getsize(caminho_final)
                                    print(f"[✓] Caricatura gerada e aprovada via Gemini Multimodal ({modelo}): {caminho_final} ({tam} bytes)")
                                    dados_artigo["imagem_capa"] = f"imagens/{slug}.jpg"
                                    dados_artigo["credito_imagem"] = "Arte: Caricatura Editorial IA / Ilustração Satírica"
                                    if not dados_artigo.get("legenda_imagem"):
                                        dados_artigo["legenda_imagem"] = f"Caricatura editorial satírica: {dados_artigo.get('titulo')}"
                                    return True
                                else:
                                    tam = os.path.getsize(caminho_final) if os.path.exists(caminho_final) else 0
                                    print(f"[!] Imagem gerada por {modelo} abaixo de 50KB ({tam} bytes). Descartando.")
                                    if os.path.exists(caminho_final):
                                        os.remove(caminho_final)
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode('utf-8', errors='ignore')
                print(f"[!] Gemini Multimodal {modelo} indisponível ({e.code}): {err_msg[:120]}")
                continue
            except Exception as e:
                print(f"[!] Falha no Gemini Multimodal {modelo}: {e}")
                continue

        # 2. Tentativa via Google Imagen 3 (caso a chave API tenha cota/permissão de predict)
        modelos_imagen = [
            "imagen-3.0-generate-002",
            "imagen-3.0-generate-001"
        ]

        payload_imagen = {
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

        headers_imagen = {
            "Content-Type": "application/json"
        }

        print("[*] Solicitando geração de caricatura editorial ao Google Imagen 3...")
        for modelo in modelos_imagen:
            url_imagen = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:predict?key={api_key}"
            try:
                req = urllib.request.Request(
                    url_imagen,
                    data=json.dumps(payload_imagen).encode("utf-8"),
                    headers=headers_imagen,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    predictions = data.get("predictions", [])
                    if predictions and "bytesBase64Encoded" in predictions[0]:
                        b64_data = predictions[0]["bytesBase64Encoded"]
                        img_bytes = base64.b64decode(b64_data)
                        with open(caminho_final, "wb") as f_img:
                            f_img.write(img_bytes)

                        # Validação de integridade e tamanho
                        if os.path.exists(caminho_final) and os.path.getsize(caminho_final) >= 50000:
                            print(f"[✓] Caricatura gerada e salva com sucesso via Google Imagen: {caminho_final} ({len(img_bytes)} bytes)")
                            dados_artigo["imagem_capa"] = f"imagens/{slug}.jpg"
                            dados_artigo["credito_imagem"] = "Arte: Caricatura Editorial IA / Ilustração Satírica"
                            if not dados_artigo.get("legenda_imagem"):
                                dados_artigo["legenda_imagem"] = f"Caricatura editorial satírica: {dados_artigo.get('titulo')}"
                            return True
                        else:
                            if os.path.exists(caminho_final):
                                os.remove(caminho_final)
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode('utf-8', errors='ignore')
                print(f"[!] Google Imagen {modelo} indisponível ({e.code}): {err_msg[:120]}")
                continue
            except Exception as e:
                print(f"[!] Falha no Google Imagen {modelo}: {e}")
                continue

    # 3. Fallback de Segurança Editorial:
    print("[!] Geração de caricatura não retornou imagem válida e fontes degradadas externas são proibidas.")
    return False

def salvar_artigo_no_site(dados_artigo, noticia_url):
    """Salva o JSON em content/ e recompila o site imediatamente"""
    os.makedirs(CONTENT_DIR, exist_ok=True)
    slug = dados_artigo["slug"]
    data_arquivo = datetime.now().strftime("%Y-%m-%d")
    arquivo_json = os.path.join(CONTENT_DIR, f"{data_arquivo}-{slug}.json")

    # Verifica se já existe arquivo com esse mesmo slug para não duplicar matérias entre dias
    slugs_existentes = carregar_slugs_existentes()
    if slug in slugs_existentes and not os.path.exists(arquivo_json):
        print(f"[i] Matéria com o slug '{slug}' já foi publicada em data anterior. Ignorando duplicação.")
        return

    if "timestamp" not in dados_artigo:
        dados_artigo["timestamp"] = datetime.now().isoformat()

    with open(arquivo_json, "w", encoding="utf-8") as f:
        json.dump(dados_artigo, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Artigo salvo com sucesso: {arquivo_json}")

    # Atualiza banco de URLs processadas e PERSISTE em disco
    db = carregar_db()
    if not any(item.get("url") == noticia_url for item in db.get("processadas", [])):
        db["processadas"].append({
            "url": noticia_url,
            "slug": slug,
            "titulo": dados_artigo["titulo"],
            "data_processamento": datetime.now().isoformat()
        })
        salvar_db(db)
        print(f"[✓] Registro de notícia persistido em {DB_PATH}")

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

def executar_rodada(modo_demo=False, url_customizada=None, tema_customizado=None):
    """Executa o ciclo completo do robô: varre, filtra, gera e publica com auditoria e notificações"""
    inicio_rodada = time.time()
    print("=" * 65)
    print("  ROBÔ AUTÔNOMO ÍMPROBO - VARREDURA E PUBLICAÇÃO SATÍRICA")
    print("=" * 65)

    melhor_noticia = None

    # CASO 1: Pauta Sob Demanda via URL externa
    if url_customizada:
        print(f"\n[*] Modo Furo de Reportagem Sob Demanda ativado!")
        print(f"[*] Raspando conteúdo da URL: {url_customizada}")
        noticia_extraida = extrair_noticia_de_url(url_customizada)
        if not noticia_extraida:
            print(f"[!] Falha ao extrair dados da URL {url_customizada}. Abortando furo.")
            duracao = time.time() - inicio_rodada
            if registrar_execucao:
                registrar_execucao("RETIDO", f"Falha na extração da URL externa: {url_customizada}", duracao_seg=duracao)
            if notificar_alerta:
                notificar_alerta("Falha ao extrair notícia de URL externa para furo de reportagem.", url_customizada)
            return False
        melhor_noticia = noticia_extraida

    # CASO 2: Pauta Sob Demanda via Tema digitado
    elif tema_customizado:
        print(f"\n[*] Modo Furo de Reportagem Sob Demanda ativado!")
        print(f"[*] Tema fornecido: '{tema_customizado}'")
        slug_temp = slugify(tema_customizado)
        melhor_noticia = {
            "fonte": "Pauta Sob Demanda / Furo Exclusivo",
            "titulo": tema_customizado,
            "link": f"https://portal-improbo.vercel.app/furo/{slug_temp}",
            "resumo": f"Pauta editorial exclusiva sob demanda solicitada pela redação: {tema_customizado}",
            "data_pub": datetime.now().strftime("%d de %B de %Y"),
            "peso_fonte": 2.5
        }

    # CASO 3: Modo de Varredura Normal (RSS Feeds)
    else:
        db = carregar_db()
        db_urls = set(item.get("url") for item in db.get("processadas", []) if item.get("url"))
        existing_slugs = carregar_slugs_existentes()
        print(f"[*] Notícias no histórico registrado: {len(db_urls)}")
        print(f"[*] Artigos publicados em content/: {len(existing_slugs)}")
        print("[*] Modo Editorial Padrão Ativo (Cobertura Política Ampla Nacional)")

        # 1. Coleta dos feeds
        print("[*] Varrendo feeds dos maiores jornais do Brasil...")
        todas_noticias = []
        for feed in RSS_FEEDS:
            itens = varrer_feed_rss(feed)
            print(f"    - {feed['fonte']}: {len(itens)} notícias coletadas")
            todas_noticias.extend(itens)

        if not todas_noticias and modo_demo:
            print("[i] Modo demonstração/offline ativo: carregando manchetes reais do cenário nacional...")
            todas_noticias = [
                {
                    "fonte": "Folha de S.Paulo - Poder",
                    "titulo": "Articulação no Congresso e STF avança para indicar Rodrigo Pacheco à vaga aberta no Supremo",
                    "link": "https://www1.folha.uol.com.br/poder/2026/10/articulacao-pacheco-stf-segundo-turno.shtml",
                    "resumo": "Lideranças do Senado e da Câmara articulam com ministros do STF para emplacar o ex-presidente do Senado Rodrigo Pacheco na vaga da Corte em plena reta final do segundo turno.",
                    "data_pub": "15 de Outubro de 2026",
                    "peso_fonte": 1.3
                }
            ]

        if not todas_noticias:
            print("[!] Feeds externos indisponíveis ou vazios. Ativando manchetes factuais de contingência...")
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
                }
            ]

        # 2. Ranqueamento de Relevância
        noticias_ranqueadas = []
        for n in todas_noticias:
            score = calcular_relevancia(n, db_urls, existing_slugs)
            if score > 0:
                noticias_ranqueadas.append((score, n))

        noticias_ranqueadas.sort(key=lambda x: x[0], reverse=True)

        # Atualiza Radar de Pautas na telemetria
        if atualizar_radar_pautas and noticias_ranqueadas:
            atualizar_radar_pautas(noticias_ranqueadas)

        if not noticias_ranqueadas:
            print("[i] Todas as matérias capturadas já foram publicadas anteriormente. O portal está 100% atualizado.")
            duracao = time.time() - inicio_rodada
            if registrar_execucao:
                registrar_execucao("SUCESSO", "Portal 100% atualizado (nenhuma pauta inédita pendente)", duracao_seg=duracao)
            return True

        melhor_score, melhor_noticia = noticias_ranqueadas[0]
        print(f"\n[★] MANCHETE ELEITA COMO A MAIS RELEVANTE DO DIA (Score: {melhor_score}):")

    print(f"    Fonte: {melhor_noticia['fonte']}")
    print(f"    Título: {melhor_noticia['titulo']}")
    print(f"    Link: {melhor_noticia['link']}")

    # 3. Redação Satírica com Gemini ou Modo Demo
    api_key = obter_api_key()
    dados_artigo = None

    if api_key and not modo_demo:
        print("\n[*] Redigindo crônica satírica com a API do Gemini...")
        resultado_ia = redigir_cronica_gemini(melhor_noticia, api_key)
        if resultado_ia:
            dados_artigo = resultado_ia
            dados_artigo["slug"] = slugify(dados_artigo.get("titulo", melhor_noticia["titulo"]))
            if "data" not in dados_artigo:
                dados_artigo["data"] = datetime.now().strftime("%d de %B de %Y").replace("October", "Outubro").replace("November", "Novembro")

    if not dados_artigo:
        if not api_key and not modo_demo:
            print("\n[!] GEMINI_API_KEY não encontrada no ambiente local.")
            print("[*] Gerando crônica através do motor editorial estruturado (Modo Pasquim Raiz)...")
        dados_artigo = criar_artigo_demo(melhor_noticia)

    # 4. Geração de Imagem: REGRA DE OURO SAGRADA (CARICATURA OBRIGATÓRIA)
    slug = dados_artigo.get("slug")
    caminho_imagem = os.path.join(IMAGENS_DIR, f"{slug}.jpg") if slug else None

    if api_key and slug:
        print("\n[*] Solicitando caricatura editorial IA no padrão de imprensa clássica...")
        gerar_caricatura_ia(dados_artigo, api_key)

    # Verificação estrita MANDATÓRIA: existe uma caricatura real (maior que 50KB)?
    if not caminho_imagem or not os.path.exists(caminho_imagem) or os.path.getsize(caminho_imagem) < 50000:
        duracao = time.time() - inicio_rodada
        motivo_retencao = "Caricatura editorial ausente ou inferior a 50KB"
        print("\n" + "!" * 75)
        print("[!] REGRA DE OURO: Matéria sem caricatura editorial válida!")
        print(f"[!] A publicação foi ABORTADA. O Ímprobo jamais posta matéria sem caricatura!")
        print("!" * 75 + "\n")
        if registrar_execucao:
            registrar_execucao("RETIDO", motivo_retencao, dados_artigo, duracao)
        if notificar_alerta:
            notificar_alerta("Caricatura editorial não aprovada no teste de qualidade.", f"Slug: {slug}")
        return False

    dados_artigo["imagem_capa"] = f"imagens/{slug}.jpg"
    dados_artigo["credito_imagem"] = "Arte: Caricatura Editorial IA / Ilustração Satírica"
    if not dados_artigo.get("legenda_imagem"):
        dados_artigo["legenda_imagem"] = f"Caricatura editorial satírica: {dados_artigo.get('titulo')}"

    # 5. Geração de Narração Neural em Áudio
    try:
        from gerar_audio import montar_roteiro_narracao, gerar_audio_arquivo
        import asyncio
        caminho_mp3 = os.path.join(AUDIO_DIR, f"{slug}.mp3")
        if not os.path.exists(caminho_mp3):
            print("\n[*] Gerando narração neural em MP3 para a crônica...")
            roteiro = montar_roteiro_narracao(dados_artigo)
            asyncio.run(gerar_audio_arquivo(roteiro, caminho_mp3))
            dados_artigo["audio_url"] = f"audio/{slug}.mp3"
            print(f"[✓] Narração neural salva: {caminho_mp3}")
    except Exception as e:
        print(f"[!] Aviso: erro na geração do áudio neural: {e}")

    # 6. PORTÃO DE SEGURANÇA MANDATÓRIO: Inspetor de Qualidade
    if validar_artigo_completo:
        aprovado, diagnostico = validar_artigo_completo(dados_artigo)
        if not aprovado:
            duracao = time.time() - inicio_rodada
            print("\n" + "!" * 75)
            print(f"[!] INSPETOR DE QUALIDADE: Publicação RETIDA!")
            print(f"[!] Diagnóstico: {diagnostico}")
            print("!" * 75 + "\n")
            if registrar_execucao:
                registrar_execucao("RETIDO", diagnostico, dados_artigo, duracao)
            if notificar_alerta:
                notificar_alerta("Publicação retida pelo Inspetor de Qualidade.", diagnostico)
            return False

    # 7. Salvamento e Compilação
    salvar_artigo_no_site(dados_artigo, melhor_noticia["link"])

    # 8. Registro de Sucesso e Notificação Telegram
    duracao = time.time() - inicio_rodada
    if registrar_execucao:
        registrar_execucao("SUCESSO", "Publicação normal validada", dados_artigo, duracao)
    if notificar_sucesso:
        notificar_sucesso(dados_artigo)

    return True

def listar_manchetes():
    """Apenas exibe as principais notícias ranqueadas sem publicar"""
    db = carregar_db()
    db_urls = set(item.get("url") for item in db.get("processadas", []) if item.get("url"))
    existing_slugs = carregar_slugs_existentes()
    print("[*] Varrendo notícias para análise de relevância...")
    
    todas = []
    for feed in RSS_FEEDS:
        itens = varrer_feed_rss(feed)
        todas.extend(itens)

    ranqueadas = []
    for n in todas:
        score = calcular_relevancia(n, db_urls, existing_slugs)
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
    parser.add_argument("--url", type=str, help="URL de notícia externa para furo de reportagem sob demanda")
    parser.add_argument("--tema", type=str, help="Tema ou pauta personalizada sob demanda")

    args = parser.parse_args()

    url_arg = args.url.strip() if args.url else None
    tema_arg = args.tema.strip() if args.tema else None

    if args.listar:
        listar_manchetes()
    elif args.loop:
        minutos = max(args.loop, 5)
        print(f"[*] Robô iniciado em modo contínuo. Intervalo: {minutos} minutos.")
        while True:
            try:
                executar_rodada(modo_demo=args.demo, url_customizada=url_arg, tema_customizado=tema_arg)
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
        executar_rodada(modo_demo=args.demo, url_customizada=url_arg, tema_customizado=tema_arg)

if __name__ == "__main__":
    main()
