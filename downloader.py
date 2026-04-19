import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import subprocess
import threading
import os
import re
import urllib.request
import zipfile

# Görünüm Ayarları
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MegaDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Media Master Pro")
        self.geometry("600x550")

        # --- Arayüz ---
        ctk.CTkLabel(self, text="Media Master", font=("Arial", 28, "bold")).pack(pady=25)
        
        # Senin istediğin o sade kontrol mesajı burada görünecek
        self.check_label = ctk.CTkLabel(self, text="Sistem kontrol ediliyor...", text_color="gray")
        self.check_label.pack(pady=5)

        self.entry = ctk.CTkEntry(self, placeholder_text="Link Yapıştır...", width=480, height=40)
        self.entry.pack(pady=10)

        self.mode_var = ctk.StringVar(value="video")
        self.radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_frame.pack(pady=10)
        ctk.CTkRadioButton(self.radio_frame, text="Video (MP4)", variable=self.mode_var, value="video").pack(side="left", padx=20)
        ctk.CTkRadioButton(self.radio_frame, text="Müzik (MP3)", variable=self.mode_var, value="audio").pack(side="left", padx=20)

        self.progress_label = ctk.CTkLabel(self, text="İşlem bekleniyor...", font=("Arial", 12))
        self.progress_label.pack(pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self, width=450)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.path_btn = ctk.CTkButton(self, text="📁 Kayıt Yerini Seç", command=self.select_folder)
        self.path_btn.pack(pady=15)
        self.folder_path = ""

        # Başta tıklanamaz, kontrol bitince açılacak
        self.download_btn = ctk.CTkButton(self, text="İNDİRMEYİ BAŞLAT", command=self.start_download, height=50, state="disabled")
        self.download_btn.pack(pady=20)

        # OTOMATİK KONTROLÜ BAŞLAT
        threading.Thread(target=self.auto_setup, daemon=True).start()

    def auto_setup(self):
        """yt-dlp ve ffmpeg'i sessizce kuran o meşhur fonksiyon"""
        ytdlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        ffmpeg_url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.4.1/ffmpeg-4.4.1-win-64.zip"
        
        # Dosyalar eksik mi?
        need_ytdlp = not os.path.exists("yt-dlp.exe")
        need_ffmpeg = not os.path.exists("ffmpeg.exe")

        if need_ytdlp or need_ffmpeg:
            self.check_label.configure(text="Gerekli bileşenler kuruluyor...", text_color="orange")
            try:
                # yt-dlp indir
                if need_ytdlp:
                    urllib.request.urlretrieve(ytdlp_url, "yt-dlp.exe")
                
                # ffmpeg indir ve zipten çıkar
                if need_ffmpeg:
                    urllib.request.urlretrieve(ffmpeg_url, "ffmpeg.zip")
                    with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
                        zip_ref.extractall(".")
                    if os.path.exists("ffmpeg.zip"):
                        os.remove("ffmpeg.zip")
                
                self.check_label.configure(text="Gerekli bileşenler hazır.", text_color="green")
            except:
                self.check_label.configure(text="Bağlantı hatası! İnternetinizi kontrol edin.", text_color="red")
                return
        else:
            self.check_label.configure(text="Gerekli bileşenler hazır.", text_color="green")
        
        # Her şey tamamsa butonu aktif et
        self.download_btn.configure(state="normal")

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.progress_label.configure(text="Kayıt yeri hazır.")

    def start_download(self):
        url = self.entry.get()
        if not url or not self.folder_path:
            messagebox.showwarning("Uyarı", "Link veya Klasör eksik!")
            return
        self.download_btn.configure(state="disabled")
        threading.Thread(target=self.run_download, args=(url,), daemon=True).start()

    def run_download(self, url):
        mode = self.mode_var.get()
        # Uygulamanın olduğu klasördeki bileşenleri kullan
        cmd = ["yt-dlp.exe", "--newline", "--progress", "--ffmpeg-location", ".", "--ignore-errors"]
        
        if mode == "audio":
            cmd += ["-x", "--audio-format", "mp3", "--embed-thumbnail", "--add-metadata", "--ppa", "thumbnailsconvertor:-vf crop='ih:ih'"]
        else:
            cmd += ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]

        cmd += ["-o", f"{self.folder_path}/%(title)s.%(ext)s", url]

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                   universal_newlines=True, startupinfo=startupinfo, encoding='utf-8')

        for line in process.stdout:
            if '[download]' in line and '%' in line:
                try:
                    percent_str = re.search(r'(\d+\.\d+)%', line).group(1)
                    self.progress_bar.set(float(percent_str) / 100)
                    self.progress_label.configure(text=f"İndiriliyor: %{percent_str}")
                except: pass

        process.wait()
        self.download_btn.configure(state="normal")
        if process.returncode == 0:
            self.progress_label.configure(text="Tamamlandı!", text_color="green")
            messagebox.showinfo("Başarılı", "İşlem bitti.")

if __name__ == "__main__":
    app = MegaDownloader()
    app.mainloop()
