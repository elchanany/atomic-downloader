import customtkinter as ctk
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from downloader_logic import Downloader
from cookie_manager import CookieManager
from localization import get_str
from utils import detect_site_info
import time

# --- Extreme Cyber Theme ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue") 

# Cyber Palette
C_BG = "#050505"       # Almost Black
C_CARD = "#121212"     # Dark Grey
C_ACCENT = "#00E5FF"   # Neon Cyan (General)
C_PH_ACCENT = "#FF9000"# Neon Orange (PH)
C_YT_ACCENT = "#FF0040"# Neon Red (YT)
C_TEXT = "#FFFFFF"     # White
C_SUBTEXT = "#888888"  # Grey
C_SUCCESS = "#00FF66"  # Neon Green
C_ERROR = "#FF0033"    # Neon Red

# Fonts
F_HEADER = ("Impact", 32)
F_SUB = ("Segoe UI", 12)
F_MAIN = ("Segoe UI", 16)
F_BOLD = ("Segoe UI", 16, "bold")
F_DIGITAL = ("Consolas", 20, "bold") # Monospaced for stats

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(get_str("app_title"))
        self.geometry("1000x800")
        self.minsize(900, 700)
        self.configure(fg_color=C_BG)

        # Variables
        self.url_var = tk.StringVar()
        self.url_var.trace("w", self.on_url_change)
        self.save_path_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.cookies_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value=get_str("status_ready"))
        self.is_log_expanded = False
        
        self.downloader = Downloader()
        self.cookie_manager = CookieManager()

        # Layout Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_ui()

    def _build_ui(self):
        # 1. Header (Cyber Style)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        
        # Title (RTL: Title on Right)
        ctk.CTkLabel(header_frame, text=get_str("header_title"), font=F_HEADER, text_color=C_ACCENT).pack(side="right")
        ctk.CTkLabel(header_frame, text=" // ", font=F_HEADER, text_color=C_SUBTEXT).pack(side="right")
        ctk.CTkLabel(header_frame, text="SYSTEM", font=F_HEADER, text_color="white").pack(side="right")

        # Subtitle
        ctk.CTkLabel(header_frame, text=get_str("header_subtitle").upper(), font=("Segoe UI", 10, "bold"), text_color=C_SUBTEXT).pack(side="right", padx=10, anchor="s", pady=5)

        # 2. Main Input Deck
        self.deck = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=20, border_color="#333", border_width=1)
        self.deck.grid(row=1, column=0, sticky="ew", padx=40, pady=10)
        self.deck.grid_columnconfigure(1, weight=1)

        # URL Entry (Center)
        self.entry_url = ctk.CTkEntry(self.deck, textvariable=self.url_var, height=60, font=("Segoe UI", 18), 
                                    placeholder_text=get_str("url_placeholder"), 
                                    justify="center", fg_color="#0a0a0a", border_color="#333", border_width=2, corner_radius=10)
        self.entry_url.grid(row=0, column=1, sticky="ew", padx=20, pady=30)

        # Paste Button (Left)
        self.btn_paste = ctk.CTkButton(self.deck, text=get_str("paste_btn"), width=60, height=60, 
                                     fg_color="#222", hover_color="#333", command=self.paste_from_clipboard, corner_radius=10)
        self.btn_paste.grid(row=0, column=0, padx=(30, 0), pady=30)
        
        # Status/Detection Pill (Under Entry)
        self.lbl_detect = ctk.CTkLabel(self.deck, text="WAITING FOR TARGET", font=("Consolas", 12, "bold"), text_color=C_SUBTEXT, bg_color="transparent")
        self.lbl_detect.grid(row=1, column=1, sticky="n", pady=(0, 20))

        # 3. Smart Actions (Login / Path)
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=10)
        
        # Path Selector (Simple)
        self.btn_path = ctk.CTkButton(self.action_frame, text=f"📂 {get_str('settings_save_path')}", command=self.browse_save_path, 
                                    fg_color="transparent", border_width=1, border_color="#444", text_color="#aaa", hover_color="#222")
        self.btn_path.pack(side="left")

        # Smart Login Card (Hidden)
        self.smart_card = ctk.CTkFrame(self.action_frame, fg_color="#1a1100", border_color=C_PH_ACCENT, border_width=1, corner_radius=10)
        # Packed only when needed
        
        ctk.CTkLabel(self.smart_card, text=get_str("login_instructions"), text_color=C_PH_ACCENT, font=F_BOLD).pack(side="right", padx=15, pady=10)
        self.btn_smart = ctk.CTkButton(self.smart_card, text=get_str("login_btn"), command=self.start_login_flow,
                                     fg_color=C_PH_ACCENT, text_color="black", hover_color="#CC7200")
        self.btn_smart.pack(side="left", padx=15, pady=10)

        # 4. Progress Hud
        self.hud = ctk.CTkFrame(self, fg_color="transparent")
        self.hud.grid(row=3, column=0, sticky="ew", padx=40, pady=20)
        
        self.btn_download = ctk.CTkButton(self.hud, text=get_str("download_btn"), height=70, font=("Segoe UI", 24, "bold"), 
                                        corner_radius=15, command=self.start_download, 
                                        fg_color=C_ACCENT, text_color="black", hover_color="#00B8CC")
        self.btn_download.pack(fill="x", pady=10)

        self.lbl_status = ctk.CTkLabel(self.hud, textvariable=self.status_var, font=("Consolas", 14), text_color=C_SUBTEXT)
        self.lbl_status.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.hud, height=10, corner_radius=5, progress_color=C_ACCENT, fg_color="#222")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=20)

        # Dashboard Stats
        stats = ctk.CTkFrame(self.hud, fg_color="transparent")
        stats.pack(fill="x")
        stats.grid_columnconfigure((0,1,2), weight=1)

        def mk_stat(col, label):
             f = ctk.CTkFrame(stats, fg_color="#111", corner_radius=5, border_width=1, border_color="#222")
             f.grid(row=0, column=col, padx=5, sticky="ew")
             ctk.CTkLabel(f, text=label, font=("Segoe UI", 10), text_color="#666").pack(pady=(5,0))
             l = ctk.CTkLabel(f, text="--", font=F_DIGITAL, text_color="#ddd")
             l.pack(pady=(0,5))
             return l

        self.stat_speed = mk_stat(2, "SPEED")
        self.stat_eta = mk_stat(1, "ETA")
        self.stat_size = mk_stat(0, "SIZE")

        # 5. Logs (Bottom)
        self.log_btn = ctk.CTkButton(self, text=get_str("log_expand_btn"), command=self.toggle_logs, fg_color="transparent", text_color="#444", hover_color="#111", height=20)
        self.log_btn.grid(row=4, column=0, pady=10)
        
        self.log_frame = ctk.CTkFrame(self, fg_color="#000", height=0)
        self.log_frame.grid(row=5, column=0, sticky="nsew")
        self.log_txt = ctk.CTkTextbox(self.log_frame, font=("Consolas", 10), fg_color="transparent", text_color="#00ff00")
        self.log_txt.pack(fill="both", expand=True)

    # --- Interaction ---
    def on_url_change(self, *args):
        url = self.url_var.get()
        info = detect_site_info(url)
        
        if info:
            site, icon, is_protected = info
            self.lbl_detect.configure(text=f"DETECTED TARGET: {site.upper()} {icon}", text_color=C_SUCCESS)
            
            # Smart Color Change
            if "Pornhub" in site:
                self.entry_url.configure(border_color=C_PH_ACCENT)
                self.lbl_detect.configure(text_color=C_PH_ACCENT)
            elif "YouTube" in site:
                self.entry_url.configure(border_color=C_YT_ACCENT)
                self.lbl_detect.configure(text_color=C_YT_ACCENT)
            else:
                self.entry_url.configure(border_color=C_ACCENT)
            
            # Login Card Logic
            has_cookies = self.cookies_path_var.get() and os.path.exists(self.cookies_path_var.get())
            if is_protected and not has_cookies:
                self.smart_card.pack(side="right", fill="x", expand=True, padx=20)
            else:
                self.smart_card.pack_forget()
        else:
            self.lbl_detect.configure(text="WAITING FOR TARGET...", text_color=C_SUBTEXT)
            self.entry_url.configure(border_color="#333")
            self.smart_card.pack_forget()

    def paste_from_clipboard(self):
        try:
            self.entry_url.delete(0, 'end')
            self.entry_url.insert(0, self.clipboard_get())
        except: pass

    def browse_save_path(self):
        path = filedialog.askdirectory()
        if path: self.save_path_var.set(path)

    def toggle_logs(self):
        if self.is_log_expanded:
            self.log_frame.grid_remove()
            self.log_btn.configure(text=get_str("log_expand_btn"))
        else:
            self.log_frame.grid(row=5, column=0, sticky="nsew")
            self.log_btn.configure(text=get_str("log_collapse_btn"))
        self.is_log_expanded = not self.is_log_expanded

    # --- Logic Connecting (Same as before but linked to new UI) ---
    def start_login_flow(self):
        self.btn_smart.configure(state="disabled", text="...")
        thread = threading.Thread(target=self._run_login_thread, daemon=True)
        thread.start()

    def _run_login_thread(self):
        def status_update(msg): self.after(0, lambda: self.status_var.set(msg))
        cookie_path = self.cookie_manager.run_login_flow(status_callback=status_update)
        self.after(0, lambda: self._login_finished(cookie_path))

    def _login_finished(self, cookie_path):
        self.btn_smart.configure(state="normal", text=get_str("login_btn"))
        if cookie_path:
            self.cookies_path_var.set(cookie_path)
            self.smart_card.pack_forget()
            tk.messagebox.showinfo(get_str("login_success_title"), get_str("login_success_msg"))

    def start_download(self):
        url = self.url_var.get()
        if not url: return

        self.btn_download.configure(state="disabled", text=get_str("downloading_btn"), fg_color="#333")
        self.progress_bar.set(0)
        self.status_var.set(get_str("status_initializing"))
        
        self.downloader.download(
            url=url,
            save_path=self.save_path_var.get(),
            cookies_path=self.cookies_path_var.get(),
            progress_callback=self.update_progress,
            log_callback=self.log_message,
            finished_callback=self.on_finished,
            error_callback=self.on_error
        )

    def update_progress(self, percent, speed, eta, total):
        self.after(0, lambda: self._ui_progress(percent, speed, eta, total))

    def _ui_progress(self, p, s, e, t):
        self.progress_bar.set(p)
        self.stat_speed.configure(text=s)
        self.stat_eta.configure(text=e)
        self.stat_size.configure(text=t)
        self.status_var.set(get_str("status_downloading", percent=int(p*100)))

    def log_message(self, msg):
        self.after(0, lambda: self._ui_log(msg))

    def _ui_log(self, msg):
        self.log_txt.insert("end", str(msg)+"\n")
        self.log_txt.see("end")

    def on_finished(self):
        self.after(0, self._ui_finished)

    def _ui_finished(self):
        self.status_var.set(get_str("status_complete"))
        self.btn_download.configure(state="normal", text=get_str("download_btn"), fg_color=C_SUCCESS)
        tk.messagebox.showinfo("Success", get_str("status_complete"))

    def on_error(self, msg):
        self.after(0, lambda: self._ui_error(msg))

    def _ui_error(self, msg):
        self.status_var.set(get_str("status_error"))
        self.btn_download.configure(state="normal", text=get_str("download_btn"), fg_color=C_ERROR)
        self._ui_log(f"ERROR: {msg}")
        tk.messagebox.showerror("Error", str(msg))

if __name__ == "__main__":
    app = App()
    app.mainloop()
