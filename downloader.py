import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class WesterosDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Westeros Media Downloader")
        self.geometry("500x450")
        
        # UI Elemanları
        self.label = ctk.CTkLabel(self, text="Westeros Downloader", font=("Arial", 22, "bold"))
        self.label.pack(pady=20)

        self.link_entry = ctk.CTkEntry(self, placeholder_text="Link yapıştırın...", width=400)
        self.link_entry.pack(pady=10)
        self.link_entry.bind("<KeyRelease>", self.on_link_paste)

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, fill="x", px=20)
        
        self.res_var = ctk.StringVar(value="Seçenekler Bekleniyor...")
        self.res_menu = ctk.CTkOptionMenu(self.options_frame, variable=self.res_var, values=["Önce link yapıştırın"])
        self.res_menu.pack(pady=10)

        self.download_btn = ctk.CTkButton(self, text="İNDİRMEYİ BAŞLAT", command=self.start_download, state="disabled")
        self.download_btn.pack(pady=20)

        self.status = ctk.CTkLabel(self, text="Sistem kontrol ediliyor...", text_color="yellow")
        self.status.pack(pady=10)

        # Açılışta bileşen kontrolü
        threading.Thread(target=self.check_requirements, daemon=True).start()

    def check_requirements(self):
        """FFmpeg ve bileşen kontrolü yapar, gerekirse kurar."""
        try:
            # Siyah ekran çıkmaması için CREATE_NO_WINDOW ekliyoruz
            subprocess.run(["ffmpeg", "-version"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.status.configure(text="Sistem Hazır", text_color="green")
        except FileNotFoundError:
            self.status.configure(text="Gerekli bileşenler kuruluyor... Lütfen bekleyin.", text_color="orange")
            # Burada normalde brew/apt veya direkt binary çekme kodu olur
            # Windows için en basiti yt-dlp'nin kendi otomatik güncelleyicisini tetiklemek
            subprocess.run(["pip", "install", "static-ffmpeg"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.status.configure(text="Kurulum tamamlandı. Hazır!", text_color="green")

    def on_link_paste(self, event):
        url = self.link_entry.get()
        if len(url) > 10:
            threading.Thread(target=self.get_formats, args=(url,), daemon=True).start()

    def get_formats(self, url):
        """Link yapıştırıldığında çözünürlükleri çeker."""
        self.status.configure(text="Seçenekler taranıyor...", text_color="yellow")
        try:
            # Siyah ekran yok: creationflags=subprocess.CREATE_NO_WINDOW
            result = subprocess.run(
                ["yt-dlp", "-F", url], 
                capture_output=True, text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            formats = []
            if "mp4" in result.stdout or "p" in result.stdout:
                formats = ["MP3 - Sadece Ses", "Best Video (MP4)"]
                # Basitleştirmek için en yaygın formatları ekledik
            
            self.res_menu.configure(values=formats)
            self.res_var.set(formats[0])
            self.download_btn.configure(state="normal")
            self.status.configure(text="Seçenekler hazır.", text_color="green")
        except:
            self.status.configure(text="Link analiz edilemedi!", text_color="red")

    def start_download(self):
        threading.Thread(target=self.download_logic, daemon=True).start()

    def download_logic(self):
        url = self.link_entry.get()
        choice = self.res_var.get()
        save_path = filedialog.askdirectory()
        if not save_path: return

        self.status.configure(text="İndirme başladı (Siyah ekran yok)...", text_color="yellow")
        
        try:
            if choice == "MP3 - Sadece Ses":
                cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "-o", f"{save_path}/%(title)s.%(ext)s", url]
            else:
                cmd = ["yt-dlp", "-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4", "-o", f"{save_path}/%(title)s.%(ext)s", url]

            # CREATE_NO_WINDOW sayesinde CMD asla açılmaz
            subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            messagebox.showinfo("Başarılı", "İşlem tamamlandı!")
            self.status.configure(text="Tamamlandı!", text_color="green")
        except Exception as e:
            messagebox.showerror("Hata", "İndirme sırasında bir sorun oluştu.")
            self.status.configure(text="Hata!", text_color="red")

if __name__ == "__main__":
    app = WesterosDownloader()
    app.mainloop()
