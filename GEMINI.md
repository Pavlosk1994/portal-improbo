# Diretrizes do Projeto — ÍMPROBO

Este repositório contém o código, scrapers, motor de áudio e aplicação web do portal **ÍMPROBO** (jornalismo satírico e crônica política).

- **Repositório Git**: `Pavlosk1994/portal-improbo`
- **Deploy**: Vercel (`https://portal-improbo.vercel.app`)
- **Diretrizes e Persona**: Consulte `PROMPT_MESTRE.md` para as regras completas editoriais, estilo e caricaturas.

---

## ⚡ Protocolo Definitivo de Criação Autônoma (Zero Interrupções)

Sempre que o usuário solicitar uma nova postagem, matéria ou crônica (ex: *"crie uma matéria"*, *"poste sobre X"*, *"rode uma nova notícia"*), a IA DEVE executar o ciclo completo de ponta a ponta **de forma 100% autônoma, sem parar em momento algum para pedir confirmações, autorizações intermediárias ou "posso prosseguir?"**.

> **Comando Canônico de Execução:** Para evitar múltiplos submits e aprovações de terminal, a IA deve disparar o orquestrador unificado:
> `python3 publicar.py` (para pauta quente RSS) ou `python3 publicar.py --tema "..."` (para tema específico).
> Esse script único cuida do `git pull`, geração, áudio, caricatura, build e `git push` em um único processo.

1. **Definição da Pauta**:
   - Se o usuário forneceu um tema, fato ou link: utilize-o imediatamente.
   - Se o usuário apenas pediu para criar uma matéria sem especificar tema: selecione autonomamente a notícia mais quente dos feeds RSS (`robo.py`).

2. **Pipeline de Execução Contínua**:
   - **Redação**: Redigir a crônica satírica seguindo estritamente as regras de `PROMPT_MESTRE.md` (inversão da premissa institucional, padrão New York Times, blacklist de clichês e campo `frase_disparo_zap`).
   - **Ilustração**: Gerar/salvar a caricatura editorial 16:9 no traço clássico Mort Drucker / MAD em `imagens/[slug].jpg`.
   - **Áudio Neural**: Gerar a locução neural via Edge-TTS em `audio/[slug].mp3`.
   - **Auditoria de Qualidade**: Rodar `inspetor.py` para validar conformidade e telemetria no `status_db.json`.
   - **Compilação**: Rodar `build.py` para gerar as páginas HTML estáticas, RSS e sitemaps.

3. **Resiliência e Fallbacks**:
   - Em caso de oscilação em APIs ou rede (ex: imagem ou Edge-TTS), retentar autonomamente até 3 vezes.
   - Persistindo o problema, adotar o fallback seguro sem travar o pipeline e sem perguntar ao usuário.

4. **Publicação & Deploy Automático**:
   - Concluído o build com sucesso, realizar o `git add .`, `git commit -m "feat(editorial): publica materia [slug]"` e `git push origin master` para acionar o deploy automático na Vercel.
   - **Telegram**: Não disparar notificação no Telegram (mantido desativado por padrão).

5. **Entrega Final**:
   - Apenas ao final de todo o ciclo concluído com sucesso em produção, apresentar o resumo da matéria com o link publicado, manchete e soundbite.
