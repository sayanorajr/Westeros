import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os

class WesterosDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Westeros Media Master")
        self.geometry("500x500")
        
        # Dosyaların saklanacağı gizli yol (Masaüstünde gözükmez)
        self.app_data_path = os.path.join(os.environ['APPDATA'], 'WesterosDownloader')
        if not os.path.exists(self.app_data_path):
            os.makedirs(self.app_data_path)

        self.setup_ui()
        threading.Thread(target=self.check_system, daemon=True).start()

    def setup_ui(self):
        self.label = ctk.CTkLabel(self, text="MEDIA MASTER", font=("Arial", 24, "bold"))
        self.label.pack(pady=20)

        self.link_entry = ctk.CTkEntry(self, placeholder_text="Video linkini buraya yapıştırın...", width=400)
        self.link_entry.pack(pady=10)
        self.link_entry.bind("<KeyRelease>", self.start_format_check)

        self.format_label = ctk.CTkLabel(self, text="Format Seçin:", font=("Arial", 12))
        self.format_label.pack(pady=(10,0))

        self.res_var = ctk.StringVar(value="Önce link yapıştırın")
        self.res_menu = ctk.CTkOptionMenu(self, variable=self.res_var, values=["Bekleniyor..."], width=200)
        self.res_menu.pack(pady=10)

        self.download_btn = ctk.CTkButton(self, text="İNDİRMEYİ BAŞLAT", command=self.start_download, state="disabled", fg_color="green")
        self.download_btn.pack(pady=20)

        self.status = ctk.CTkLabel(self, text="Sistem hazırlanıyor...", text_color="gray")
        self.status.pack(pady=10)

    def check_system(self):
        """Bileşenleri APPDATA klasörüne kurar, masaüstünü kirletmez."""
        try:
            # yt-dlp ve static-ffmpeg kontrolü/kurulumu
            self.status.configure(text="Bileşenler kontrol ediliyor...")
            subprocess.run(["pip", "install", "yt-dlp", "static-ffmpeg"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.status.configure(text="Sistem Hazır", text_color="green")
        except:
            self.status.configure(text="Kurulum hatası!", text_color="red")

    def start_format_check(self, event):
        url = self.link_entry.get()
        if "http" in url and len(url) > 15:
            self.status.configure(text="Formatlar alınıyor...", text_color="yellow")
            threading.Thread(target=self.fetch_formats, args=(url,), daemon=True).start()

    def fetch_formats(self, url):
        try:
            # Sadece format listesini çeken hızlı komut
            cmd = ["yt-dlp", "-F", "--no-playlist", url]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            options = ["MP3 - Yüksek Kalite Ses"]
            if "1080p" in result.stdout: options.append("Video - 1080p (MP4)")
            if "720p" in result.stdout: options.append("Video - 720p (MP4)")
            if "480p" in result.stdout: options.append("Video - 480p (MP4)")
            
            if len(options) == 1: options.append("Video - En İyi Kalite")

            self.res_menu.configure(values=options)
            self.res_var.set(options[0])
            self.download_btn.configure(state="normal")
            self.status.configure(text="Formatlar yüklendi.", text_color="green")
        except:
            self.status.configure(text="Link geçersiz veya desteklenmiyor.", text_color="red")

    def start_download(self):
        self.download_btn.configure(state="disabled", text="İŞLENİYOR...")
        threading.Thread(target=self.download_engine, daemon=True).start()

    def download_engine(self):
        url = self.link_entry.get()
        choice = self.res_var.get()
        save_dir = filedialog.askdirectory()
        
        if not save_dir:
            self.download_btn.configure(state="normal", text="İNDİRMEYİ BAŞLAT")
            return

        try:
            if "MP3" in choice:
                cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", f"{save_dir}/%(title)s.%(ext)s", url]
            else:
                quality = "bestvideo[height<=1080]+bestaudio/best"
                if "720p" in choice: quality = "bestvideo[height<=720]+bestaudio/best"
                elif "480p" in choice: quality = "bestvideo[height<=480]+bestaudio/best"
                
                cmd = ["yt-dlp", "-f", quality, "--merge-output-format", "mp4", "-o", f"{save_dir}/%(title)s.%(ext)s", url]

            subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            messagebox.showinfo("Başarılı", "Dosya başarıyla indirildi!")
        except:
            messagebox.showerror("Hata", "İndirme tamamlanamadı.")
        
        self.download_btn.configure(state="normal", text="İNDİRMEYİ BAŞLAT")
        self.status.configure(text="Hazır")

if __name__ == "__main__":
    app = WesterosDownloader()
    app.mainloop()
