# YoutubeVideoAnalyzer

Script em Python que recebe a URL de um vídeo do YouTube e devolve um resumo do conteúdo falado nele.

Todo o processamento é local e gratuito:

1. **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** baixa o áudio do vídeo
2. **[ffmpeg](https://ffmpeg.org/)** converte o áudio para mp3
3. **[faster-whisper](https://github.com/SYSTRAN/faster-whisper)** transcreve o áudio (roda na sua máquina, sem API)
4. **[Ollama](https://ollama.com/)** (modelo `llama3.2`) gera o resumo a partir da transcrição (também local)

Nenhuma chave de API é necessária.

## Como rodar

Existem duas formas: direto na máquina (venv) ou via Docker.

### Opção 1: venv local

Pré-requisitos:
- Python 3.13+
- [ffmpeg](https://ffmpeg.org/) instalado e no PATH
- [Ollama](https://ollama.com/download) instalado e rodando

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

ollama pull llama3.2

python main.py
```

### Opção 2: Docker Compose

Pré-requisito: Docker instalado.

```powershell
docker compose up -d ollama                        # sobe o servidor Ollama
docker compose exec ollama ollama pull llama3.2     # baixa o modelo (só na primeira vez)
docker compose run --rm app                         # roda o script
```

O `docker-compose.yml` já cuida do ffmpeg, das dependências Python e da comunicação entre o script e o Ollama — não precisa instalar nada além do Docker.

## Uso

### Linha de comando

Ao rodar `python main.py`, o script pede a URL do vídeo:

```
Cole a URL do vídeo do YouTube: https://www.youtube.com/watch?v=...
```

O resumo é exibido no terminal e também salvo em `resumo.txt`.

### Interface gráfica

Também há uma interface simples em Tkinter (biblioteca padrão do Python, não precisa instalar nada a mais):

```powershell
python gui.py
```

Cole a URL, clique em "Resumir" (ou tecle Enter) e acompanhe o progresso na barra de status. O resumo aparece na caixa de texto e também é salvo em `resumo.txt`. O processamento roda em segundo plano, então a janela não trava durante o download/transcrição/resumo.

## Configuração

No topo do [main.py](main.py):

- `MODELO_WHISPER` — tamanho do modelo Whisper (`base` por padrão). Modelos maiores (`small`, `medium`) melhoram a qualidade da transcrição, mas são mais lentos em CPU.
- `MODELO_OLLAMA` — modelo usado para o resumo (`llama3.2` por padrão). Pode ser trocado por qualquer modelo disponível no Ollama, desde que seja baixado antes com `ollama pull <modelo>`.

## Estrutura do projeto

```
main.py               script principal / linha de comando
gui.py                interface gráfica (Tkinter)
requirements.txt      dependências Python
Dockerfile            imagem do script
docker-compose.yml    orquestra o script + servidor Ollama
```

## Limitações conhecidas

- O download depende do `player_client: android` do yt-dlp para contornar bloqueios de bot-detection do YouTube. Esse tipo de proteção muda com frequência; se o download parar de funcionar, pode ser necessário atualizar o yt-dlp (`pip install -U yt-dlp`) ou ajustar o client usado em `baixar_audio`.
- A qualidade do resumo depende do modelo local escolhido — modelos pequenos (como `llama3.2` 3B) são rápidos, mas menos precisos que modelos maiores ou serviços pagos.
- Processamento 100% local significa que a velocidade depende do hardware da máquina (principalmente sem GPU).
