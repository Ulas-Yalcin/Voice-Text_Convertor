import tkinter as tk
import sounddevice as sd
import wave
import speech_recognition as sr
import numpy as np
import pyperclip
from deep_translator import GoogleTranslator


class SesKaydedici:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Ses Kaydedici")
        self.root.geometry("600x600")
        self.root.config(bg="#2c2f33")

        # Değişkenler
        self.kayit = False
        self.duraklat = False
        self.frames = []
        self.fs = 44100
        self.channels = 1
        self.orjinal_text = ""
        self.cevrilmis = False

        # Başlık
        self.label = tk.Label(
            root, text="🎵 Ses Kaydedici",
            font=("Arial", 20, "bold"), fg="#ffffff", bg="#2c2f33"
        )
        self.label.pack(pady=10)

        # Kayıt durum göstergesi (ışık)
        self.status_label = tk.Label(
            root, text="●",
            font=("Arial", 40, "bold"),
            fg="red", bg="#2c2f33"
        )
        self.status_label.pack(pady=10)

        # Kaydı Başlat butonu
        self.start_btn = tk.Button(
            root, text="⏺️ Kaydı Başlat",
            command=self.kaydi_baslat,
            bg="#e74c3c", fg="white", font=("Arial", 14, "bold"),
            width=20
        )
        self.start_btn.pack(pady=10)

        # Kaydı Durdur butonu
        self.stop_btn = tk.Button(
            root, text="⏹️ Kaydı Durdur",
            command=self.kaydi_durdur,
            bg="#27ae60", fg="white", font=("Arial", 14, "bold"),
            width=20
        )
        self.stop_btn.pack(pady=10)

        # Kayda Ara Ver / Devam Et butonu
        self.pause_btn = tk.Button(
            root, text="⏸️ Kayda Ara Ver",
            command=self.kaydi_duraklat,
            bg="#f39c12", fg="white", font=("Arial", 14, "bold"),
            width=20
        )
        self.pause_btn.pack(pady=10)

        # Çıktı kutusu
        self.text_box = tk.Text(
            root, height=10, width=60,
            font=("Arial", 12),
            wrap="word", bg="#f0f0f0"
        )
        self.text_box.pack(pady=20)

        # Kopyala butonu
        self.copy_btn = tk.Button(
            root, text="📋 Kopyala",
            command=self.kopyala,
            bg="#9b59b6", fg="white", font=("Arial", 12, "bold"),
            width=15
        )
        self.copy_btn.pack(pady=5)

        # Çevir butonu
        self.translate_btn = tk.Button(
            root, text="🌍 İngilizceye Çevir",
            command=self.cevir_toggle,
            bg="#16a085", fg="white", font=("Arial", 12, "bold"),
            width=20
        )
        self.translate_btn.pack(pady=5)

        # Çıkış butonu
        self.exit_btn = tk.Button(
            root, text="🚪 Çıkış",
            command=root.quit,
            bg="#3498db", fg="white", font=("Arial", 12, "bold"),
            width=15
        )
        self.exit_btn.pack(pady=10)

    def callback(self, indata, frames, zaman, status):
        if self.kayit and not self.duraklat:
            self.frames.append(indata.copy())

    def kaydi_baslat(self):
        if not self.kayit:
            self.kayit = True
            self.frames = []
            self.stream = sd.InputStream(
                samplerate=self.fs,
                channels=self.channels,
                callback=self.callback
            )
            self.stream.start()
            self.status_label.config(fg="green")

    def kaydi_duraklat(self):
        if self.kayit:
            self.duraklat = not self.duraklat
            if self.duraklat:
                self.pause_btn.config(text="▶️ Devam Et")
                self.status_label.config(fg="orange")
            else:
                self.pause_btn.config(text="⏸️ Kayda Ara Ver")
                self.status_label.config(fg="green")

    def kaydi_durdur(self):
        if self.kayit:
            self.kayit = False
            self.stream.stop()
            self.stream.close()

            # WAV kaydet
            dosya_adi = "kayit.wav"
            data = np.concatenate(self.frames, axis=0)
            data = (data * 32767).astype(np.int16)
            wf = wave.open(dosya_adi, "wb")
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.fs)
            wf.writeframes(data.tobytes())
            wf.close()

            self.status_label.config(fg="red")

            # STT
            recognizer = sr.Recognizer()
            with sr.AudioFile(dosya_adi) as source:
                audio = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio, language="tr-TR")
            except sr.UnknownValueError:
                text = "❌ Ses anlaşılamadı."
            except sr.RequestError:
                text = "❌ Servis hatası."

            self.orjinal_text = text
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, text)

    def kopyala(self):
        text = self.text_box.get("1.0", tk.END).strip()
        pyperclip.copy(text)

    def cevir_toggle(self):
        text = self.text_box.get("1.0", tk.END).strip()
        if not text:
            return
        if not self.cevrilmis:
            try:
                translated = GoogleTranslator(source='tr', target='en').translate(text)
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, translated)
                self.translate_btn.config(text="↩️ Türkçeye Dön")
                self.cevrilmis = True
            except Exception:
                self.text_box.insert(tk.END, "\n\n⚠️ Çeviri hatası.")
        else:
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, self.orjinal_text)
            self.translate_btn.config(text="🌍 İngilizceye Çevir")
            self.cevrilmis = False


if __name__ == "__main__":
    root = tk.Tk()
    app = SesKaydedici(root)
    root.mainloop()
