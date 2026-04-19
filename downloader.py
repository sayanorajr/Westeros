import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import subprocess
import threading
import os
import re
import urllib.request
import zipfile

ctk.set_appearance_mode("Dark")

class MediaMaster(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MEDIA MASTER")
        self.geometry("600x650")
        self.configure(fg_color="#000000")

        # UI
        ctk.CTkLabel(self, text="MEDIA MASTER", font=("Helvetica", 32, "bold"), text_color="#FFFFFF").pack(pady=(40, 10))
        
        self.check_label = ctk.CTkLabel(self, text="", font=("Helvetica", 12), text_color="#888888")
        self.check_label.pack(pady=5)

        # Link Girişi ve Analiz Butonu
        self.entry = ctk.CTkEntry(self, placeholder_text="Video Linkini Yapıştırın...", width=480, height=45, 
                                 fg_color="#111111", border_color="#333333")
        self.entry.pack(pady=10)
        self.entry.bind("<KeyRelease>", self.start_analysis_thread) # Link değişince analiz başlar

        # Dinamik Seçenekler Listesi
        ctk.CTkLabel(self, text="İNDİRME SEÇENEKLERİ", font=("Helvetica", 10, "bold"), text_color="#555555").pack(pady=(10,0))
        self.format_menu = ctk.CTkOptionMenu(self, values=["Link Bekleniyor..."], width=300,
                                           fg_color="#111111", button_color="#333333", text_color="#FFFFFF")
        self.format_menu.pack(pady=10)

        # Progress
        self.progress_label = ctk.CTkLabel(self, text="Hazır", font=("Helvetica", 11), text_color="#666666")
        self.progress_label.pack(pady=(20, 0))
        self.progress_bar = ctk.CTkProgressBar(self, width=450, fg_color="#111111", progress_color="#FFFFFF")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.path_btn = ctk.CTkButton(self, text="KAYIT YERİ SEÇ", command=self.select_folder, 
                                     fg_color="transparent", border_width=1, border_color="#333333")
        self.path_btn.pack(pady=10)
        
        self.folder_path = ""
        self.download_btn = ctk.CTkButton(self, text="İNDİRMEYİ BAŞLAT", command=self.start_download, 
                                         height=55, width=300, font=("Helvetica", 16, "bold"),
                                         fg_color="#FFFFFF", text_color="#000000", state="disabled")
        self.download_btn.pack(pady=30)

        # İlk Açılış Kontrolü
        threading.Thread(target=self.initial_setup, daemon=True).start()

    def initial_setup(self):
        # Dosyaları uygulamanın kendi klasöründe (AppData veya App folder) tutar
        ytdlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        ffmpeg_url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.4.1/ffmpeg-4.4.1-win-64.zip"
        
        if not os.path.exists("yt-dlp.exe") or not os.path.exists("ffmpeg.exe"):
            self.check_label.configure(text="Gerekli bileşenler kuruluyor...")
            try:
                if not os.path.exists("yt-dlp.exe"):
                    urllib.request.urlretrieve(ytdlp_url, "yt-dlp.exe")
                if not os.path.exists("ffmpeg.exe"):
                    urllib.request.urlretrieve(ffmpeg_url, "ffmpeg.zip")
                    with zipfile.ZipFile("ffmpeg.zip", 'r') as z: z.extractall(".")
                    os.remove("ffmpeg.zip")
            except: pass
        self.check_label.configure(text="")
        self.download_btn.configure(state="normal")

    def start_analysis_thread(self, event=None):
        url = self.entry.get()
        if len(url) > 10:
            threading.Thread(target=self.analyze_link, args=(url,), daemon=True).start()

    def analyze_link(self, url):
        self.format_menu.configure(values=["Analiz ediliyor..."])
        try:
            # Mevcut formatları çek
            cmd = ["yt-dlp.exe", "-F", url]
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.check_output(cmd, startupinfo=startupinfo, text=True)
            
            options = []
            # Çözünürlükleri yakala
            if "1080p" in result: options.append("Video - 1080p (MP4)")
            if "720p" in result: options.append("Video - 720p (MP4)")
            if "480p" in result: options.append("Video - 480p (MP4)")
            options.append("Sadece Müzik (MP3)")
            
            self.format_menu.configure(values=options)
            self.format_menu.set(options[0])
        except:
            self.format_menu.configure(values=["Hatalı Link!"])

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()

    def start_download(self):
        url = self.entry.get()
        choice = self.format_menu.get()
        if not self.folder_path or "Link" in choice:
            messagebox.showwarning("Hata", "Link ve Klasör seçin!")
            return
        self.download_btn.configure(state="disabled", text="İŞLENİYOR...")
        threading.Thread(target=self.run_download, args=(url, choice), daemon=True).start()

    def run_download(self, url, choice):
        # Format Belirleme
        if "1080p" in choice: f_cmd = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best"
        elif "720p" in choice: f_cmd = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best"
        elif "480p" in choice: f_cmd = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best"
        else: f_cmd = "bestaudio/best"

        cmd = ["yt-dlp.exe", "--newline", "--progress", "--ffmpeg-location", ".", "-f", f_cmd]
        if "MP3" in choice: cmd += ["-x", "--audio-format", "mp3"]
        cmd += ["-o", f"{self.folder_path}/%(title)s.%(ext)s", "--merge-output-format", "mp4", url]

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                   universal_newlines=True, startupinfo=startupinfo, encoding='utf-8')

        for line in process.stdout:
            # İlerleme Çubuğu Tamir Edildi (Regex ile kesin çekim)
            match = re.search(r'(\d+\.\d+)%', line)
            if match:
                p = float(match.group(1))
                self.progress_bar.set(p / 100)
                self.progress_label.configure(text=f"İndiriliyor: %{p}")

        process.wait()
        self.download_btn.configure(state="normal", text="İNDİRMEYİ BAŞLAT")
        if process.returncode == 0:
            messagebox.showinfo("Başarılı", "İndirme Tamamlandı!")

if __name__ == "__main__":
    app = MediaMaster()
    app.mainloop()
