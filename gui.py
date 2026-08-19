import os
import queue
import tempfile
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from main import baixar_audio, converter_para_mp3, resumir_texto, transcrever_audio


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YoutubeVideoAnalyzer")
        self.geometry("700x500")
        self.minsize(500, 350)

        self.fila = queue.Queue()

        tk.Label(self, text="URL do vídeo do YouTube:").pack(anchor="w", padx=10, pady=(10, 0))

        frame_url = tk.Frame(self)
        frame_url.pack(fill="x", padx=10)
        self.entrada_url = tk.Entry(frame_url)
        self.entrada_url.pack(side="left", fill="x", expand=True)
        self.entrada_url.bind("<Return>", lambda evento: self.iniciar_resumo())
        self.botao_resumir = tk.Button(frame_url, text="Resumir", command=self.iniciar_resumo)
        self.botao_resumir.pack(side="left", padx=(5, 0))

        self.status = tk.Label(self, text="", anchor="w", fg="gray20")
        self.status.pack(fill="x", padx=10, pady=(5, 0))

        tk.Label(self, text="Resumo:").pack(anchor="w", padx=10, pady=(10, 0))
        self.texto_resumo = scrolledtext.ScrolledText(self, wrap="word", state="disabled")
        self.texto_resumo.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.after(100, self.processar_fila)

    def iniciar_resumo(self):
        url = self.entrada_url.get().strip()
        if not url:
            messagebox.showwarning("URL vazia", "Cole a URL de um vídeo do YouTube.")
            return

        self.botao_resumir.config(state="disabled")
        self.definir_resumo("")
        threading.Thread(target=self.executar_pipeline, args=(url,), daemon=True).start()

    def executar_pipeline(self, url: str):
        try:
            with tempfile.TemporaryDirectory() as pasta_tmp:
                self.fila.put(("status", "Baixando áudio..."))
                caminho_original = baixar_audio(url, pasta_tmp)

                self.fila.put(("status", "Convertendo áudio..."))
                caminho_mp3 = os.path.join(pasta_tmp, "audio.mp3")
                converter_para_mp3(caminho_original, caminho_mp3)

                self.fila.put(("status", "Transcrevendo áudio (Whisper local)..."))
                transcricao = transcrever_audio(caminho_mp3)

                self.fila.put(("status", "Gerando resumo (Ollama local)..."))
                resumo = resumir_texto(transcricao)

            with open("resumo.txt", "w", encoding="utf-8") as f:
                f.write(resumo)

            self.fila.put(("resumo", resumo))
            self.fila.put(("status", "Concluído. Resumo também salvo em resumo.txt"))
        except Exception as e:
            self.fila.put(("erro", str(e)))

    def processar_fila(self):
        try:
            while True:
                tipo, valor = self.fila.get_nowait()
                if tipo == "status":
                    self.status.config(text=valor)
                elif tipo == "resumo":
                    self.definir_resumo(valor)
                    self.botao_resumir.config(state="normal")
                elif tipo == "erro":
                    self.status.config(text="Erro durante o processamento.")
                    messagebox.showerror("Erro", valor)
                    self.botao_resumir.config(state="normal")
        except queue.Empty:
            pass
        self.after(100, self.processar_fila)

    def definir_resumo(self, texto: str):
        self.texto_resumo.config(state="normal")
        self.texto_resumo.delete("1.0", "end")
        self.texto_resumo.insert("1.0", texto)
        self.texto_resumo.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()
