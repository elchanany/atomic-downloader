"""
Atomic Downloader - Launcher
Main entry point: checks dependencies, runs first-time setup if needed, then launches the app.
"""
import sys
import os
import subprocess
import json
import importlib
import threading
import time

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETUP_FLAG = os.path.join(APP_DIR, '.setup_done')
VENV_DIR = os.path.join(APP_DIR, '.venv')
VERSION = "2.1.0"

# If a venv exists and we're not running from it, re-launch with the venv's Python
def ensure_venv_python():
    if not os.path.exists(VENV_DIR):
        return  # No venv, continue with system Python
    
    if sys.platform == 'win32':
        venv_python = os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join(VENV_DIR, 'bin', 'python')
    
    if not os.path.exists(venv_python):
        return  # Venv exists but no python executable found
    
    # Check if we're already running from the venv
    current_python = os.path.abspath(sys.executable)
    venv_python_abs = os.path.abspath(venv_python)
    if current_python.lower() == venv_python_abs.lower():
        return  # Already running from venv
    
    # Re-launch this script with the venv's Python
    # Use subprocess instead of os.execv (handles spaces in paths on Windows)
    script_path = os.path.abspath(sys.argv[0])
    result = subprocess.call([venv_python, script_path] + sys.argv[1:])
    sys.exit(result)

ensure_venv_python()

REQUIRED_PACKAGES = [
    ("flask", "Flask"),
    ("yt_dlp", "yt-dlp"),
    ("webview", "pywebview"),
    ("requests", "requests"),
    ("packaging", "packaging"),
    ("selenium", "selenium"),
    ("webdriver_manager", "webdriver-manager"),
]

TRANSLATIONS = {
    "en": {
        "title": "ATOMIC",
        "subtitle": "DOWNLOADER // FIRST RUN SETUP",
        "deps_title": "DEPENDENCIES",
        "install_btn": "INSTALL",
        "installing": "INSTALLING...",
        "launch_btn": "LAUNCH APP",
        "retry_btn": "RETRY",
        "log_title": " INSTALL LOG",
        "status_ok": "OK",
        "status_missing": "MISSING",
        "status_failed": "FAILED",
        "all_ok": "All dependencies installed!",
        "already_installed": "already installed",
        "installing_pkg": "Installing",
        "setup_complete": "Setup complete! Launching app...",
        "some_failed": "Some packages failed:",
    },
    "he": {
        "title": "ATOMIC",
        "subtitle": "מוריד אטומי // הגדרה ראשונית",
        "deps_title": "תלויות (DEPENDENCIES)",
        "install_btn": "התקן",
        "installing": "מתקין...",
        "launch_btn": "הפעל יישום",
        "retry_btn": "נסה שוב",
        "log_title": " יומן התקנה",
        "status_ok": "תקין",
        "status_missing": "חסר",
        "status_failed": "נכשל",
        "all_ok": "כל התלויות הותקנו בהצלחה!",
        "already_installed": "כבר מותקן",
        "installing_pkg": "מתקין את",
        "setup_complete": "ההתקנה הסתיימה! מפעיל...",
        "some_failed": "חלק מהחבילות נכשלו:",
    }
}

# All supported languages for dropdown
LANG_OPTIONS_DATA = [
    ("en", "English"),
    ("he", "עברית"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("ru", "Русский"),
    ("ar", "العربية"),
    ("zh-CN", "简体中文"),
    ("zh-TW", "繁體中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("pt", "Português"),
    ("it", "Italiano"),
    ("nl", "Nederlands"),
    ("tr", "Türkçe"),
    ("pl", "Polski"),
    ("id", "Bahasa Indonesia"),
    ("hi", "हिन्दी"),
    ("vi", "Tiếng Việt"),
    ("th", "ไทย"),
    ("sv", "Svenska"),
    ("da", "Dansk"),
    ("no", "Norsk"),
    ("fi", "Suomi"),
    ("el", "Ελληνικά"),
    ("cs", "Čeština"),
    ("hu", "Magyar"),
    ("ro", "Română"),
    ("uk", "Українська"),
    ("bg", "Български"),
    ("hr", "Hrvatski"),
    ("sr", "Српски"),
    ("sk", "Slovenčina"),
    ("ca", "Català"),
    ("tl", "Filipino"),
    ("ms", "Bahasa Melayu"),
    ("fa", "فارسی"),
    ("sw", "Kiswahili"),
    ("ta", "தமிழ்"),
    ("te", "తెలుగు"),
    ("ur", "اردو"),
    ("bn", "বাংলা"),
    ("mr", "मराठी"),
    ("gu", "ગુજરાતી"),
    ("pa", "ਪੰਜਾਬੀ"),
    ("kn", "ಕನ್ನಡ"),
    ("ml", "മലയാളം"),
]

LANG_OPTIONS = [f"{name} ({code})" for code, name in LANG_OPTIONS_DATA]
LANG_MAP = {f"{name} ({code})": code for code, name in LANG_OPTIONS_DATA}

selected_lang_code = "en"  # Default to English


def check_dependencies():
    """Return list of (import_name, pip_name) that are missing."""
    # Invalidate import caches so newly installed packages are found
    importlib.invalidate_caches()
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(import_name)
        except ImportError:
            # Fallback: check via pip show (handles path/cache issues)
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'show', pip_name],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    missing.append((import_name, pip_name))
            except Exception:
                missing.append((import_name, pip_name))
    return missing


def is_first_run():
    """Check if this is the first run (setup not completed)."""
    return not os.path.exists(SETUP_FLAG)


def mark_setup_done():
    with open(SETUP_FLAG, 'w') as f:
        json.dump({"version": VERSION, "setup": True}, f)


def run_app(lang_code="en"):
    """Launch the main app with pywebview."""
    from app import app as flask_app
    import webview
    import requests as req

    def start_server():
        flask_app.run(port=5000, use_reloader=False)

    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Wait for Flask to be ready
    for _ in range(30):
        try:
            r = req.get('http://127.0.0.1:5000', timeout=1)
            if r.status_code == 200:
                break
        except:
            pass
        time.sleep(0.3)

    # Pass language to app via query param only on first run (setup)
    url = 'http://127.0.0.1:5000/'
    if lang_code:
        url += f'?lang={lang_code}'

    icon_path = os.path.join(APP_DIR, 'static', 'images', 'logo.png')
    # icon=icon_path, # Icon not supported in this pywebview version
    window = webview.create_window(
        title='Atomic Downloader',
        url=url,
        resizable=True,
        background_color='#050505'
    )
    # --- Fix Taskbar Icon for Windows ---
    try:
        import ctypes
        from ctypes import windll
        
        # 1. Set AppUserModelID (groups taskbar icon)
        myappid = 'atomic.downloader.app.2.1.0'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        # 2. Force Window Icon via SendMessage (retry loop)
        def set_icon():
            ico_path = os.path.join(APP_DIR, 'static', 'images', 'logo.ico')
            if not os.path.exists(ico_path):
                print(f"Icon file not found: {ico_path}")
                return
                
            # Try for up to 5 seconds to find the window
            hwnd = 0
            for i in range(10):
                time.sleep(0.5)
                hwnd = windll.user32.FindWindowW(None, "Atomic Downloader")
                if hwnd:
                    break
            
            if hwnd:
                ICON_SMALL = 0
                ICON_BIG = 1
                WM_SETICON = 0x0080
                LR_LOADFROMFILE = 0x0010
                IMAGE_ICON = 1
                
                hIcon = windll.user32.LoadImageW(None, ico_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE)
                if hIcon:
                    windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hIcon)
                    windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hIcon)
                    # Force redraw
                    windll.user32.RedrawWindow(hwnd, None, None, 0x0400 | 0x0001)
                else:
                    print("Failed to load icon image via LoadImageW")
            else:
                 print("Could not find window 'Atomic Downloader' to set icon")

        threading.Thread(target=set_icon, daemon=True).start()
    except Exception as e:
        print(f"Icon setup exception: {e}")

    flask_app.window = window
    webview.start()
    sys.exit()


# ============================================================
# FIRST-RUN SETUP UI (tkinter - always available in Python)
# ============================================================

def run_setup_ui(missing_packages):
    import tkinter as tk
    from tkinter import font as tkfont
    from tkinter import ttk

    global selected_lang_code

    BG = '#0a0a0a'
    BG_CARD = '#111111'
    CYAN = '#00f3ff'
    GREEN = '#00ff6a'
    RED = '#ff003c'
    DIM = '#666666'
    WHITE = '#ffffff'
    PINK = '#ff00cc'

    root = tk.Tk()
    root.title('Atomic Downloader - Setup')
    root.configure(bg=BG)
    root.geometry('560x650')
    root.resizable(False, False)

    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 280
    y = (root.winfo_screenheight() // 2) - 325
    root.geometry(f'+{x}+{y}')

    # Fonts
    try:
        title_font = tkfont.Font(family='Consolas', size=22, weight='bold')
        sub_font = tkfont.Font(family='Consolas', size=9)
        label_font = tkfont.Font(family='Segoe UI', size=11)
        small_font = tkfont.Font(family='Segoe UI', size=9)
        log_font = tkfont.Font(family='Consolas', size=8)
        btn_font = tkfont.Font(family='Consolas', size=13, weight='bold')
    except:
        title_font = ('Consolas', 22, 'bold')
        sub_font = ('Consolas', 9)
        label_font = ('Segoe UI', 11)
        small_font = ('Segoe UI', 9)
        log_font = ('Consolas', 8)
        btn_font = ('Consolas', 13, 'bold')
    
    # UI Elements references for translation updates
    ui_refs = {}

    # --- Language Selector (Top Right) ---
    top_frame = tk.Frame(root, bg=BG)
    top_frame.pack(fill='x', padx=10, pady=5)
    
    lang_var = tk.StringVar(value="English (en)")

    def on_lang_change(event):
        global selected_lang_code
        val = lang_var.get()
        selected_lang_code = LANG_MAP.get(val, "en")
        update_texts()

    lang_combo = ttk.Combobox(top_frame, textvariable=lang_var, values=LANG_OPTIONS, state="readonly", width=15)
    lang_combo.pack(side='right')
    lang_combo.bind("<<ComboboxSelected>>", on_lang_change)
    
    # --- Header ---
    header = tk.Frame(root, bg=BG)
    header.pack(fill='x', pady=(10, 5))

    title_lbl = tk.Label(header, text='ATOMIC', font=title_font, fg=CYAN, bg=BG)
    title_lbl.pack()
    subtitle_lbl = tk.Label(header, text='DOWNLOADER // FIRST RUN SETUP', font=sub_font, fg=DIM, bg=BG)
    subtitle_lbl.pack()
    
    ui_refs['title'] = title_lbl
    ui_refs['subtitle'] = subtitle_lbl

    # --- Separator ---
    sep = tk.Frame(root, bg=CYAN, height=1)
    sep.pack(fill='x', padx=40, pady=(15, 20))

    # --- Package list card ---
    card = tk.Frame(root, bg=BG_CARD, highlightbackground='#222', highlightthickness=1)
    card.pack(fill='x', padx=30, pady=(0, 10))

    deps_lbl = tk.Label(card, text='DEPENDENCIES', font=small_font, fg=CYAN, bg=BG_CARD, anchor='w')
    deps_lbl.pack(fill='x', padx=15, pady=(12, 5))
    ui_refs['deps_title'] = deps_lbl

    # Package status labels
    pkg_labels = {}
    all_packages = [pip_name for _, pip_name in REQUIRED_PACKAGES]

    for pip_name in all_packages:
        row = tk.Frame(card, bg=BG_CARD)
        row.pack(fill='x', padx=15, pady=2)

        is_missing = pip_name in [p for _, p in missing_packages]
        status_text = 'MISSING' if is_missing else 'OK'
        status_color = RED if is_missing else GREEN

        name_lbl = tk.Label(row, text=f'  {pip_name}', font=label_font, fg=WHITE, bg=BG_CARD, anchor='w')
        name_lbl.pack(side='left')

        status_lbl = tk.Label(row, text=status_text, font=small_font, fg=status_color, bg=BG_CARD, anchor='e')
        status_lbl.pack(side='right')

        pkg_labels[pip_name] = status_lbl

    tk.Frame(card, bg=BG_CARD, height=10).pack()  # padding

    # --- Current action label ---
    action_var = tk.StringVar(value='')
    action_label = tk.Label(root, textvariable=action_var, font=small_font, fg=PINK, bg=BG)
    action_label.pack(pady=(5, 5))

    # --- Log area ---
    log_frame = tk.Frame(root, bg='#000000', highlightbackground='#222', highlightthickness=1)
    log_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))

    log_title_lbl = tk.Label(log_frame, text=' INSTALL LOG', font=small_font, fg=DIM, bg='#000000', anchor='w')
    log_title_lbl.pack(fill='x', padx=8, pady=(5, 0))
    ui_refs['log_title'] = log_title_lbl

    log_text = tk.Text(log_frame, bg='#000000', fg=GREEN, font=log_font,
                       height=8, wrap='word', bd=0, insertbackground=GREEN,
                       state='disabled', relief='flat')
    log_text.pack(fill='both', expand=True, padx=8, pady=(2, 8))

    def add_log(msg):
        log_text.config(state='normal')
        log_text.insert('end', msg + '\n')
        log_text.see('end')
        log_text.config(state='disabled')

    # --- Install button ---
    btn_frame = tk.Frame(root, bg=BG)
    btn_frame.pack(fill='x', padx=30, pady=(0, 25))

    install_btn = tk.Button(
        btn_frame,
        text='INSTALL',
        font=btn_font,
        fg='#000000',
        bg=CYAN,
        activebackground='#00d4ff',
        activeforeground='#000',
        relief='flat',
        cursor='hand2',
        height=1,
        bd=0,
    )
    install_btn.pack(fill='x', ipady=6)
    ui_refs['install_btn'] = install_btn

    
    # Track button/label states for reliable language switching
    btn_state = {'mode': 'install'}  # 'install', 'installing', 'launch', 'retry'
    pkg_states = {pip_name: ('missing' if pip_name in [p for _, p in missing_packages] else 'ok') 
                  for _, pip_name in REQUIRED_PACKAGES}

    def get_text(key):
        return TRANSLATIONS.get(selected_lang_code, TRANSLATIONS['en']).get(key, key)

    def update_texts():
        ui_refs['title'].config(text=get_text('title'))
        ui_refs['subtitle'].config(text=get_text('subtitle'))
        ui_refs['deps_title'].config(text=get_text('deps_title'))
        ui_refs['log_title'].config(text=get_text('log_title'))
        
        # Update button text based on tracked state
        state_to_key = {
            'install': 'install_btn',
            'installing': 'installing',
            'launch': 'launch_btn',
            'retry': 'retry_btn',
        }
        key = state_to_key.get(btn_state['mode'], 'install_btn')
        install_btn.config(text=get_text(key))
            
        # Update status labels based on tracked state
        for pip_name, lbl in pkg_labels.items():
            state = pkg_states.get(pip_name, 'ok')
            state_key = {'ok': 'status_ok', 'missing': 'status_missing', 
                        'failed': 'status_failed', 'installing': 'installing'}.get(state, 'status_ok')
            lbl.config(text=get_text(state_key))

    setup_success = [False]

    def run_install():
        btn_state['mode'] = 'installing'
        install_btn.config(state='disabled', text=get_text('installing'), bg=DIM)

        def install_thread():
            pip_exe = sys.executable

            for import_name, pip_name in REQUIRED_PACKAGES:
                # Check if already installed
                try:
                    importlib.import_module(import_name)
                    pkg_states[pip_name] = 'ok'
                    root.after(0, lambda pn=pip_name: action_var.set(f'{pn} ... {get_text("already_installed")}'))
                    root.after(0, lambda pn=pip_name: pkg_labels[pn].config(text=get_text('status_ok'), fg=GREEN))
                    root.after(0, lambda pn=pip_name: add_log(f'[{get_text("status_ok")}] {pn} {get_text("already_installed")}'))
                    continue
                except ImportError:
                    pass

                pkg_states[pip_name] = 'installing'
                root.after(0, lambda pn=pip_name: action_var.set(f'{get_text("installing_pkg")} {pn}...'))
                root.after(0, lambda pn=pip_name: pkg_labels[pn].config(text=get_text("installing"), fg=CYAN))
                root.after(0, lambda pn=pip_name: add_log(f'[>>] pip install {pn}'))

                try:
                    result = subprocess.run(
                        [pip_exe, '-m', 'pip', 'install', pip_name],
                        capture_output=True, text=True, timeout=120
                    )
                    if result.returncode == 0:
                        pkg_states[pip_name] = 'ok'
                        root.after(0, lambda pn=pip_name: pkg_labels[pn].config(text=get_text('status_ok'), fg=GREEN))
                        root.after(0, lambda pn=pip_name: add_log(f'[{get_text("status_ok")}] {pn} installed successfully'))
                    else:
                        pkg_states[pip_name] = 'failed'
                        root.after(0, lambda pn=pip_name: pkg_labels[pn].config(text=get_text('status_failed'), fg=RED))
                        root.after(0, lambda pn=pip_name, err=result.stderr[:200]: add_log(f'[ERR] {pn}: {err}'))
                except Exception as e:
                    pkg_states[pip_name] = 'failed'
                    root.after(0, lambda pn=pip_name: pkg_labels[pn].config(text=get_text('status_failed'), fg=RED))
                    root.after(0, lambda pn=pip_name, err=str(e): add_log(f'[ERR] {pn}: {err}'))

            # Check if all installed now
            still_missing = check_dependencies()
            if not still_missing:
                btn_state['mode'] = 'launch'
                root.after(0, lambda: action_var.set(get_text('all_ok')))
                root.after(0, lambda: add_log(f'\n[DONE] {get_text("setup_complete")}'))
                root.after(0, lambda: install_btn.config(text=get_text('launch_btn'), bg=GREEN, state='normal'))
                setup_success[0] = True
                root.after(0, lambda: install_btn.config(command=lambda: finish_setup()))
            else:
                btn_state['mode'] = 'retry'
                names = ', '.join([p for _, p in still_missing])
                root.after(0, lambda: action_var.set(f'{get_text("some_failed")} {names}'))
                root.after(0, lambda: install_btn.config(text=get_text('retry_btn'), bg=RED, state='normal'))
                root.after(0, lambda: install_btn.config(command=run_install))

        threading.Thread(target=install_thread, daemon=True).start()

    def finish_setup():
        mark_setup_done()
        root.destroy()

    install_btn.config(command=run_install)

    # Initial text update
    update_texts()

    # If nothing is missing, auto-complete
    if not missing_packages:
        btn_state['mode'] = 'launch'
        action_var.set(get_text('all_ok'))
        install_btn.config(text=get_text('launch_btn'), bg=GREEN, command=finish_setup)
        for pip_name in all_packages:
            pkg_states[pip_name] = 'ok'
            pkg_labels[pip_name].config(text=get_text('status_ok'), fg=GREEN)
        add_log(f'[{get_text("status_ok")}] {get_text("all_ok")}')

    root.mainloop()
    return setup_success[0] or not missing_packages


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    # Initial check
    missing = check_dependencies()

    if is_first_run() or missing:
        success = run_setup_ui(missing)
        if not success:
            sys.exit(1)

    # Re-check after setup
    still_missing = check_dependencies()
    if still_missing:
        names = ', '.join([p for _, p in still_missing])
        print(f"[ERROR] Missing packages: {names}")
        print("Please install manually: pip install " + ' '.join([p for _, p in still_missing]))
        sys.exit(1)

    # Launch the app
    # Only pass selected_lang_code if it was determined during THIS setup run
    # Otherwise pass None so the app uses its stored preference
    lang_to_pass = selected_lang_code if (is_first_run() or missing) else None
    run_app(lang_to_pass)
