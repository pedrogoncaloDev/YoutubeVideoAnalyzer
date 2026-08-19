import os
import sys
import tempfile

import ffmpeg
import ollama
import yt_dlp
from faster_whisper import WhisperModel

MODELO_WHISPER = "base"  # roda em CPU; use "small"/"medium" para mais qualidade
MODELO_OLLAMA = "llama3.2"


def baixar_audio(url: str, pasta_destino: str) -> str:
    opcoes = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(pasta_destino, "audio_original.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        # client "web" leva a 403 nos formatos atuais; "android" contorna isso
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def converter_para_mp3(caminho_entrada: str, caminho_saida: str) -> None:
    (
        ffmpeg
        .input(caminho_entrada)
        .output(caminho_saida, acodec="libmp3lame", audio_bitrate="128k")
        .overwrite_output()
        .run(quiet=True)
    )


def transcrever_audio(caminho_mp3: str) -> str:
    modelo = WhisperModel(MODELO_WHISPER, device="cpu", compute_type="int8")
    segmentos, _ = modelo.transcribe(caminho_mp3)
    return " ".join(segmento.text.strip() for segmento in segmentos)


def resumir_texto(transcricao: str) -> str:
    resposta = ollama.chat(
        model=MODELO_OLLAMA,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você resume transcrições de vídeos do YouTube em português, "
                    "de forma clara e organizada em tópicos."
                ),
            },
            {"role": "user", "content": f"Resuma esta transcrição:\n\n{transcricao}"},
        ],
    )
    return resposta["message"]["content"]


def main() -> None:
    # evita "caracteres quebrados" no console do Windows com acentos
    sys.stdout.reconfigure(encoding="utf-8")

    url = input("Cole a URL do vídeo do YouTube: ").strip()

    with tempfile.TemporaryDirectory() as pasta_tmp:
        print("Baixando áudio...")
        caminho_original = baixar_audio(url, pasta_tmp)

        print("Convertendo áudio...")
        caminho_mp3 = os.path.join(pasta_tmp, "audio.mp3")
        converter_para_mp3(caminho_original, caminho_mp3)

        print("Transcrevendo áudio (Whisper local)...")
        transcricao = transcrever_audio(caminho_mp3)

        print("Gerando resumo (Ollama local)...")
        resumo = resumir_texto(transcricao)

    print("\n=== RESUMO ===\n")
    print(resumo)

    with open("resumo.txt", "w", encoding="utf-8") as f:
        f.write(resumo)
    print("\n(resumo também salvo em resumo.txt)")


if __name__ == "__main__":
    main()
