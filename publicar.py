#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE DE PUBLICAÇÃO 100% AUTÔNOMO - PORTAL ÍMPROBO
Executa todo o ciclo de vida da matéria em um único comando:
1. Sincronização prévia com o Git remoto (evita conflitos com GitHub Actions)
2. Geração da crônica, caricatura, áudio e compilação do site (via robo.py)
3. Commit e Push direto para a Vercel
"""

import sys
import subprocess
import argparse
import robo

def rodar_cmd(cmd, desc=""):
    """Executa um comando de sistema e reporta erro se houver"""
    if desc:
        print(f"[*] {desc}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Erro em {desc or cmd}: {res.stderr.strip()[:200]}")
    return res.returncode == 0, res.stdout.strip()

def sincronizar_git_remoto():
    """Garante que a base local está sincronizada com o GitHub antes de publicar"""
    print("\n[1/3] Sincronizando com o repositório remoto (GitHub)...")
    rodar_cmd("git fetch origin master", "Buscando atualizações remotas")
    # Tenta merge simples ou pull
    rodar_cmd("git pull origin master --no-rebase -X ours", "Atualizando branch local")

def publicar_git():
    """Faz commit e push de todas as alterações geradas pela nova matéria"""
    print("\n[3/3] Publicando alterações no GitHub & Vercel...")
    sucesso_add, _ = rodar_cmd("git add .", "Adicionando arquivos modificados")
    if not sucesso_add:
        return False
    
    # Identifica última matéria gerada para a mensagem de commit
    _, status = rodar_cmd("git status --porcelain", "Checando status")
    if not status:
        print("[*] Nenhuma alteração detectada para commit.")
        return True

    sucesso_commit, _ = rodar_cmd(
        'git commit -m "feat(editorial): publica nova materia autonoma [skip ci]"',
        "Criando commit"
    )
    
    sucesso_push, out_push = rodar_cmd("git push origin master", "Enviando para a master (Deploy Vercel)")
    if sucesso_push:
        print("[✓] Deploy disparado com sucesso na Vercel!")
        # Sincroniza main se existir
        rodar_cmd("git push origin master:main", "Sincronizando branch main")
        return True
    else:
        # Se foi rejeitado por descompasso, tenta um pull reconciliador e retenta o push
        print("[!] Push inicial recusado. Reconciliando com o remoto...")
        rodar_cmd("git pull origin master --no-rebase -X ours", "Reconciliando")
        sucesso_push_retry, _ = rodar_cmd("git push origin master", "Retentando push")
        return sucesso_push_retry

def main():
    parser = argparse.ArgumentParser(description="Publicador 100% Autônomo do ÍMPROBO")
    parser.add_argument("--tema", type=str, default=None, help="Tema ou manchete específica sob demanda")
    parser.add_argument("--url", type=str, default=None, help="URL de notícia para furo de reportagem")
    args = parser.parse_args()

    print("=" * 65)
    print("  ÍMPROBO — PIPELINE DE PUBLICAÇÃO 100% AUTÔNOMO (ZERO CLIQUES)")
    print("=" * 65)

    # 1. Sincroniza Git primeiro para evitar conflitos
    sincronizar_git_remoto()

    # 2. Executa a rodada do robô (Redação + Arte MAD + Áudio Edge-TTS + Inspetor + Build)
    print("\n[2/3] Executando redação, arte, áudio e build...")
    sucesso_robo = robo.executar_rodada(
        url_customizada=args.url,
        tema_customizado=args.tema
    )

    if not sucesso_robo:
        print("\n[!] A geração da matéria não foi concluída com sucesso pelo robô. Abortando deploy.")
        sys.exit(1)

    # 3. Faz o deploy no Git
    sucesso_deploy = publicar_git()
    if not sucesso_deploy:
        print("\n[!] Falha ao subir alterações para o Git. Verifique as credenciais.")
        sys.exit(1)

    print("\n" + "=" * 65)
    print("  [✓] MATÉRIA CRIADA E PUBLICADA COM SUCESSO NA VERCEL!")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
