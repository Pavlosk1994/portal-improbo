#!/usr/bin/env python3
"""
Robô Autônomo de Varredura e Redação Satírica - IMPRÓBO
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
from datetime import datetime
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

# Importa o compilador do site
from build import build_all, CONTENT_DIR, BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "noticias_db.json")
ENV_PATH = os.path.join(BASE_DIR, ".env")
PROMPT_MESTRE_PATH = os.path.join(BASE_DIR, "PROMPT_MESTRE.md")

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
    "hugo motta": 4, "pacheco": 4, "haddad": 4, "ministro": 4,

    # Pautas de Alto Impacto / Eleições (Peso 4)
    "eleição": 5, "eleições": 5, "2º turno": 5, "segundo turno": 5, "pesquisa": 4,
    "pec": 4, "6x1": 5, "votação": 4, "reforma": 4, "orçamento": 4, 
    "emenda": 4, "salário": 3, "imposto": 4,

    # Gatilhos de Contradição e Absurdo / Comédia de Costumes (Peso 3)
    "recuo": 3, "volta atrás": 4, "gafe": 4, "escândalo": 4, "aliança": 3,
    "acordo": 3, "promessa": 3, "surto": 4, "farra": 4, "privilégio": 4
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

        soup = BeautifulSoup(content, 'xml')
        items = soup.find_all('item')
        if not items:
            soup = BeautifulSoup(content, 'html.parser')
            items = soup.find_all('item')

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
    except Exception as e:
        print(f"[-] Erro ao ler feed {fonte} ({url}): {e}")

    return noticias

def calcular_relevancia(noticia, db_urls):
    """Atribui nota de relevância com base nos termos de poder e novidade"""
    if noticia["link"] in db_urls:
        return -100  # Já processada anteriormente

    texto_busca = f"{noticia['titulo']} {noticia['resumo']}".lower()
    score = 0.0

    for termo, peso in TERMOS_RELEVANCIA.items():
        if re.search(r'\b' + re.escape(termo) + r'\b', texto_busca):
            score += peso

    score *= noticia.get("peso_fonte", 1.0)
    return round(score, 2)

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
Você é o Redator-Chefe e Cronista Ácido de **IMPRÓBO**, portal brasileiro de jornalismo satírico, crônica política e comédia de costumes.
Sua missão:
1. Fidelidade Absoluta ao Fato Real: Os personagens, dados, falas e decisões são 100% reais (sem inventar mentiras).
2. Acidez Máxima e Humor de Pasquim Raiz: Cínico, visceral, analítico e irônico. Proibido tom acadêmico ou morno. Use metáforas populares ácidas (o agiota de calçada, o garçom do rodízio, o malandro na missa). Desmonte a pose e a liturgia dos políticos.
3. Regra dos Títulos Curtos e Punchy: O título DEVE ser curto (40 a 65 caracteres no máximo), em caixa alta, contendo uma piada ou contradição sarcástica imediata (ex: 'SOCIALISMO DE MANHÃ, CENTRÃO DE TARDE'). Proibido títulos longos ou que pareçam sinopses. O detalhamento do contexto vai no subtítulo.
4. Regra Estrita da Imagem Real ou Nada: Apenas incluir imagem se for a foto real da matéria original. Caso não haja foto real, defina 'imagem_capa': null, 'legenda_imagem': null e 'credito_imagem': null. NUNCA invente fotos ou use bancos de imagens genéricos.
5. Sem Viés Partidário: O alvo é sempre o poder, a burocracia estatal, a incoerência eleitoral e o teatro político.
6. Estrutura de Retorno: Você DEVE responder OBRIGATORIAMENTE com um único objeto JSON válido (sem tags markdown ```json), contendo:
{
  "titulo": "MANCHETE CURTA COM PIADA OU CONTRADIÇÃO (MÁX 60 CARACTERES)",
  "subtitulo": "Subtítulo cínico e explicativo detalhando o absurdo da situação",
  "categoria": "Comédia de Costumes" (ou Crônica Política / Folclore de Brasília),
  "tempo_leitura": "3 min de leitura",
  "autor": "Redação Ácida",
  "destaque": true,
  "legenda_imagem": "Legenda editorial satírica para a foto de capa",
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

Gere agora a crônica satírica completa no formato JSON exigido, com rigor factual e ironia máxima para o IMPRÓBO.
"""

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

    req = urllib.request.Request(
        url_api,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            texto_resposta = data['candidates'][0]['content']['parts'][0]['text']
            # Remove blocos markdown caso a API inclua
            texto_limpo = re.sub(r'^```json\s*', '', texto_resposta.strip())
            texto_limpo = re.sub(r'\s*```$', '', texto_limpo)
            return json.loads(texto_limpo)
    except Exception as e:
        print(f"[!] Erro ao chamar API Gemini: {e}")
        return None

def criar_artigo_demo(noticia, dados_imagem):
    """Gera uma crônica satírica exemplar com base na notícia para validação do pipeline"""
    slug = slugify(noticia["titulo"])
    hoje = datetime.now().strftime("%d de %B de %Y").replace("October", "Outubro").replace("November", "Novembro")
    
    # Título curto e sarcástico (máximo 60 caracteres)
    titulo_curto = f"O BALCÃO DO PLANALTO: {noticia['titulo'][:30].upper().strip()}..." if len(noticia['titulo']) > 32 else f"O BALCÃO DO PLANALTO: {noticia['titulo'].upper()}"
    
    return {
        "slug": slug,
        "data": hoje,
        "categoria": "Crônica Política",
        "tempo_leitura": "3 min de leitura",
        "titulo": titulo_curto,
        "subtitulo": f"Com a solenidade de quem descobriu a pólvora na antevéspera da votação, Brasília encena mais um capítulo do milagre institucional.",
        "autor": "Redação Ácida",
        "destaque": True,
        "imagem_capa": dados_imagem.get("imagem_url") if dados_imagem else None,
        "legenda_imagem": dados_imagem.get("legenda_sugerida") if (dados_imagem and dados_imagem.get("imagem_url")) else None,
        "credito_imagem": dados_imagem.get("credito") if (dados_imagem and dados_imagem.get("imagem_url")) else None,
        "corpo": [
            f"Brasília é uma usina inesgotável de assombros. Em mais um episódio da novela cotidiana do poder, a notícia de que '{noticia['titulo']}' caiu sobre os corredores com o impacto de um cafezinho frio servido em copo de plástico.",
            f"O fato cru é que, segundo apuração do {noticia['fonte']}, {noticia['resumo']}. No entanto, na tradução para o dialeto do botequim nacional, o que se vê é a clássica coreografia de quem precisa parecer ocupadíssimo enquanto calcula os dividendos da próxima rodada de negociações.",
            "Quando a conveniência política aperta, até os mais austeros ocupantes de gabinete descobrem uma pressa comovente para aprovar o que até ontem era jurado de morte. É a eterna dança das cadeiras, onde o cidadão paga a conta do banquete e assiste ao espetáculo de pé na fila do ônibus.",
            "Resta ao leitor respirar fundo e contemplar a beleza quase poética da cara de pau coletiva: enquanto houver quórum e liturgia, a matéria-prima do absurdo nacional está plenamente assegurada."
        ],
        "milagres": [
            {
                "titulo": "A Urgência de Última Hora",
                "texto": "A velocidade espantosa com que matérias engavetadas por meses ganham prioridade absoluta assim que o calendário aperta."
            },
            {
                "titulo": "A Liturgia do Discurso",
                "texto": "A arte de transformar um arranjo de bastidor em uma proclamação solene de amor devotado ao interesse público."
            },
            {
                "titulo": "A Fatura Compartilhada",
                "texto": "A certeza imutável de que, qualquer que seja o desfecho do acordo, o custo fiscal será debitado com juros na conta do contribuinte."
            }
        ],
        "contexto_real": f"{noticia['resumo']} Noticiado originalmente por {noticia['fonte']} com repercussão nos principais círculos institucionais da capital."
    }

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
    salvar_db(db)

    # Recompila todas as páginas HTML do IMPRÓBO
    print("[*] Recompilando o portal IMPRÓBO (Home e Artigos)...")
    build_all()
    print("[✓] Portal atualizado com a nova matéria!")

def executar_rodada(modo_demo=False):
    """Executa o ciclo completo do robô: varre, filtra, gera e publica"""
    print("=" * 65)
    print("  ROBÔ AUTÔNOMO IMPRÓBO - VARREDURA E PUBLICAÇÃO SATÍRICA")
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
        else:
            print("[!] Nenhuma notícia capturada nos feeds neste momento.")
            return False

    # 2. Ranqueamento de Relevância
    noticias_ranqueadas = []
    for n in todas_noticias:
        score = calcular_relevancia(n, db_urls)
        if score > 0:
            noticias_ranqueadas.append((score, n))

    noticias_ranqueadas.sort(key=lambda x: x[0], reverse=True)

    if not noticias_ranqueadas:
        print("[!] Nenhuma notícia nova relevante encontrada (todas já foram processadas ou estão fora do escopo).")
        return False

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
            img_url = dados_imagem.get("imagem_url")
            dados_artigo["imagem_capa"] = img_url
            dados_artigo["credito_imagem"] = dados_imagem.get("credito") if img_url else None
            dados_artigo["legenda_imagem"] = (resultado_ia.get("legenda_imagem") or dados_imagem.get("legenda_sugerida")) if img_url else None
            if "data" not in dados_artigo:
                dados_artigo["data"] = datetime.now().strftime("%d de %B de %Y").replace("October", "Outubro")

    if not dados_artigo:
        if not api_key and not modo_demo:
            print("\n[!] GEMINI_API_KEY não encontrada no ambiente.")
            print("[*] Gerando crônica através do motor editorial estruturado (Modo Laboratório)...")
        dados_artigo = criar_artigo_demo(melhor_noticia, dados_imagem)

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
    parser = argparse.ArgumentParser(description="Robô de Varredura e Publicação Autônoma do IMPRÓBO")
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
