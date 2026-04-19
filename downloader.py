import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("green")

class SocialDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Social Audio Downloader v1.0")
        self.geometry("450x350")

        self.label = ctk.CTkLabel(self, text="Social MP3 Downloader", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.link_entry = ctk.CTkEntry(self, placeholder_text="Link yapıştır (IG, TikTok, YT...)", width=350)
        self.link_entry.pack(pady=10)

        self.download_btn = ctk.CTkButton(self, text="MP3 OLARAK İNDİR", command=self.start_thread, font=("Arial", 14, "bold"))
        self.download_btn.pack(pady=20)

        self.status = ctk.CTkLabel(self, text="Hazır", text_color="gray")
        self.status.pack(pady=10)

    def start_thread(self):
        thread = threading.Thread(target=self.download_logic)
        thread.start()

    def download_logic(self):
        url = self.link_entry.get()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen bir link girin!")
            return

        save_path = filedialog.askdirectory(title="Kaydedilecek Klasörü Seç")
        if not save_path: return

        self.status.configure(text="İndiriliyor... Lütfen bekleyin.", text_color="yellow")
        self.download_btn.configure(state="disabled")

        try:
            cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "-o", f"{save_path}/%(title)s.%(ext)s", url]
            subprocess.run(cmd, check=True)
            self.status.configure(text="Başarıyla İndirildi!", text_color="green")
            messagebox.showinfo("Başarılı", "Müzik kaydedildi!")
        except Exception as e:
            self.status.configure(text="Hata oluştu!", text_color="red")
            messagebox.showerror("Hata", "İndirme başarısız!")
        
        self.download_btn.configure(state="normal")
        self.link_entry.delete(0, 'end')

if __name__ == "__main__":
    app = SocialDownloader()
    app.mainloop()
