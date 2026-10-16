#!/usr/bin/env python3
"""
Gerador de Áudio Neural - IMPRÓBO
Utiliza Edge-TTS com a voz neural brasileira 'pt-BR-AntonioNeural'
para narrar as crônicas satíricas completas em arquivos MP3 de alta fidelidade.
"""

import os
import sys
import json
import glob
import asyncio
import argparse

# Garante acesso aos pacotes instalados no usuário
sys.path.insert(0, os.path.expanduser("~/.local/lib/python3.12/site-packages"))

try:
    import edge_tts
except ImportError:
    print("[!] Erro: edge-tts não está instalado. Execute: pip install --user edge-tts")
    edge_tts = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

VOZ_PADRAO = "pt-BR-AntonioNeural"  # Voz jornalística e dramática em português do Brasil

def montar_roteiro_narracao(artigo):
    """
    Constrói a narrativa fluida para a voz neural:
    Abertura editorial, título, subtítulo, corpo da crônica,
    Manual de Emergência e vinheta final de encerramento.
    """
    blocos = []
    
    # Vinheta de Abertura
    blocos.append(f"IMPRÓBO apresenta.")
    blocos.append(f"{artigo.get('titulo')}.")
    
    sub = artigo.get('subtitulo', '').strip()
    if sub:
        blocos.append(sub)
    
    # Corpo da Crônica
    for paragrafo in artigo.get('corpo', []):
        p_limpo = paragrafo.strip()
        if p_limpo:
            blocos.append(p_limpo)
            
    # Guia de Sobrevivência
    guia = artigo.get('guia_sobrevivencia') or artigo.get('milagres', [])
    if guia:
        blocos.append("Manual de Emergência. Guia de sobrevivência do otário.")
        for idx, item in enumerate(guia, start=1):
            t = item.get('titulo', '').strip()
            txt = item.get('texto', '').strip()
            blocos.append(f"Dica {idx}: {t}. {txt}")
            
    # Encerramento Editorial
    blocos.append("Esta foi mais uma crônica ácida do IMPRÓBO. Nenhum fato foi distorcido: o absurdo da realidade brasileira já veio pronto de fábrica.")
    
    return "\n\n".join(blocos)

async def gerar_audio_arquivo(texto, arquivo_saida, voz=VOZ_PADRAO):
    """Gera o arquivo de áudio MP3 utilizando a API do Edge-TTS"""
    if not edge_tts:
        raise RuntimeError("edge-tts não está disponível")
        
    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)
    comunicador = edge_tts.Communicate(texto, voz, rate="+2%", pitch="-1Hz")
    await comunicador.save(arquivo_saida)

def processar_artigo(caminho_json, forcar=False):
    """Lê o JSON do artigo e gera o MP3 correspondente na pasta audio/"""
    with open(caminho_json, "r", encoding="utf-8") as f:
        artigo = json.load(f)
        
    slug = artigo.get("slug")
    if not slug:
        print(f"[-] Artigo sem slug: {caminho_json}")
        return False
        
    arquivo_mp3 = os.path.join(AUDIO_DIR, f"{slug}.mp3")
    
    if os.path.exists(arquivo_mp3) and not forcar:
        print(f"[i] Áudio já existe: {slug}.mp3 (use --forcar para sobrescrever)")
        # Garante que o campo audio_url está preenchido no JSON
        if not artigo.get("audio_url"):
            artigo["audio_url"] = f"audio/{slug}.mp3"
            with open(caminho_json, "w", encoding="utf-8") as f:
                json.dump(artigo, f, indent=2, ensure_ascii=False)
        return True
        
    roteiro = montar_roteiro_narracao(artigo)
    print(f"[*] Gerando narração neural para: {artigo.get('titulo')[:50]}...")
    
    try:
        asyncio.run(gerar_audio_arquivo(roteiro, arquivo_mp3))
        tam_kb = os.path.getsize(arquivo_mp3) / 1024
        print(f"    [✓] Concluído: {arquivo_mp3} ({tam_kb:.1f} KB)")
        
        # Atualiza o JSON do artigo
        artigo["audio_url"] = f"audio/{slug}.mp3"
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(artigo, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"    [!] Erro ao gerar áudio de {slug}: {e}")
        return False

def gerar_todos(forcar=False):
    """Varre todos os JSONs em content/ e gera o áudio neural correspondente"""
    arquivos = sorted(glob.glob(os.path.join(CONTENT_DIR, "*.json")))
    print(f"[*] Encontrados {len(arquivos)} artigos em content/")
    sucessos = 0
    for arq in arquivos:
        if processar_artigo(arq, forcar=forcar):
            sucessos += 1
    print(f"\n[✓] Processamento concluído: {sucessos}/{len(arquivos)} áudios disponíveis em {AUDIO_DIR}")

def main():
    parser = argparse.ArgumentParser(description="Gerador de Áudio Neural das Crônicas do IMPRÓBO")
    parser.add_argument("--slug", help="Gera áudio apenas para o artigo com o slug especificado")
    parser.add_argument("--forcar", action="store_true", help="Regera áudio mesmo se o arquivo já existir")
    args = parser.parse_args()
    
    if args.slug:
        arquivos = glob.glob(os.path.join(CONTENT_DIR, f"*{args.slug}*.json"))
        if not arquivos:
            print(f"[!] Nenhum artigo encontrado com o slug '{args.slug}'")
            sys.exit(1)
        processar_artigo(arquivos[0], forcar=args.forcar)
    else:
        gerar_todos(forcar=args.forcar)

if __name__ == "__main__":
    main()

