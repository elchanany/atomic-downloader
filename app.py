from flask import Flask, render_template, jsonify, request
import os
import sys
import threading
import time
from downloader_logic import Downloader
from cookie_manager import CookieManager
from utils import detect_site_info
import logging

# Suppress Flask CLI logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Disable caching so pywebview always loads fresh JS/CSS
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# --- Global State ---
STATE = {
    "status": "idle", # idle, downloading, error, finished
    "percent": 0.0,
    "speed": "--",
    "eta": "--",
    "eta_seconds": None,
    "total": "--",
    "logs": [],
    "error_msg": "",
    "cookies_path": "",
    "save_path": os.path.expanduser("~/Downloads"),
    "history": [], # List of finished downloads
    "title": ""
}

# Load cookies if exist on startup
if os.path.exists("cookies.txt"):
    STATE["cookies_path"] = os.path.abspath("cookies.txt")
    STATE["logs"].append("AUTH: Auto-loaded saved cookies.")

downloader = Downloader()
cookie_manager = CookieManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/detect', methods=['POST'])
def detect():
    data = request.json
    text = data.get('url', '')
    # Just check the first line for detection
    first_url = text.split('\n')[0].strip()
    
    info = detect_site_info(first_url)
    if info:
        site, icon, is_protected = info
        has_cookies = bool(STATE["cookies_path"] and os.path.exists(STATE["cookies_path"]))
        return jsonify({"site": site, "icon": icon, "protected": is_protected, "has_cookies": has_cookies})
    return jsonify({"site": None})

@app.route('/api/formats', methods=['POST'])
def get_formats():
    data = request.json
    url = data.get('url', '').strip()
    if not url:
        return jsonify({"formats": []})
    
    formats = downloader.probe_formats(url)
    return jsonify({"formats": formats})

@app.route('/api/login', methods=['POST'])
def login():
    def run_login():
        def callback(msg):
            STATE["logs"].append(f"AUTH: {msg}")
        
        path = cookie_manager.run_login_flow(status_callback=callback)
        if path:
            STATE["cookies_path"] = path
            STATE["logs"].append("AUTH: Login Successful!")
        else:
            STATE["logs"].append("AUTH: Login Failed.")

    threading.Thread(target=run_login).start()
    return jsonify({"status": "started"})

@app.route('/api/choose_folder', methods=['POST'])
def choose_folder():
    try:
        if not hasattr(app, 'window'):
            return jsonify({"path": ""})
            
        # Open folder dialog via pywebview
        result = app.window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            return jsonify({"path": result[0]})
        return jsonify({"path": ""})
    except Exception as e:
        print(f"Error choosing folder: {e}")
        return jsonify({"path": ""})

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.json
    text = data.get('url', '')
    quality = data.get('quality', 'best')
    advanced = data.get('advanced', {})
    
    # Split by newlines for batch
    urls = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not urls:
        return jsonify({"error": "No URL provided"}), 400

    STATE["percent"] = 0
    STATE["error_msg"] = ""
    STATE["title"] = ""
    
    # Update save path if provided
    if "savePath" in advanced and advanced["savePath"]:
        STATE["save_path"] = advanced["savePath"]

    def run_batch():
        def progress_cb(info):
            STATE["status"] = info.get("status", "downloading")
            STATE["percent"] = info.get("percent", 0)
            STATE["speed"] = info.get("speed", "")
            STATE["eta"] = info.get("eta", "")
            STATE["eta_seconds"] = info.get("eta_seconds")
            STATE["total"] = info.get("total", "")
            STATE["playlist_index"] = info.get("playlist_index")
            STATE["playlist_count"] = info.get("playlist_count")
            if info.get("title"):
                STATE["title"] = info.get("title")
        
        def log_cb(msg):
            STATE["logs"].append(msg)
            if "has already been downloaded" in msg:
                STATE["status"] = "finished"
                STATE["percent"] = 1.0

        def finish_cb(info):
            # info contains filename, title, thumbnail
            
            # Verify file exists and has size > 0
            fn = info.get('filename')
            if fn and os.path.exists(fn):
                size = os.path.getsize(fn)
                if size == 0:
                    error_cb(f"Download failed: File {os.path.basename(fn)} is empty.")
                    return
            else:
                 # Check if it might be a merger issue where temp file is gone but final exists
                 # But info['filename'] should be the final one from hooks.
                 # Let's start with a warning if missing
                 log_cb(f"[WARN] File not found immediately: {fn}")

            STATE["history"].insert(0, info) # Add to top
            log_cb(f"[DONE] Finished: {info['title']}")
            
            # Close the overall batch if this was the last item
            if info.get('index', 0) + 1 == info.get('total', 1):
                 STATE["status"] = "finished"
                 STATE["percent"] = 1.0
        
        def error_cb(msg):
            STATE["status"] = "error"
            STATE["error_msg"] = msg
            STATE["logs"].append(f"ERROR: {msg}")

        try:
            downloader.download(
                urls=urls,
                save_path=STATE["save_path"],
                cookies_path=STATE["cookies_path"],
                quality=quality,
                advanced=advanced,
                progress_callback=progress_cb,
                log_callback=log_cb,
                finished_callback=finish_cb,
                error_callback=error_cb
            )
        except Exception as e:
            error_cb(str(e))

    threading.Thread(target=run_batch).start()
    
    # FIX: Set status immediately to prevent "Cancelled" flash on frontend
    STATE["status"] = "starting"
    STATE["percent"] = 0
    
    return jsonify({"status": "started"})

@app.route('/api/status')
def get_state():
    state_copy = STATE.copy()
    state_copy["logs"] = STATE["logs"][-50:]
    return jsonify(state_copy)

@app.route('/api/cancel', methods=['POST'])
def cancel_download():
    """Cancel the currently running download."""
    if STATE["status"] == "downloading":
        downloader.cancel_requested = True
        STATE["status"] = "idle"
        STATE["percent"] = 0
        STATE["logs"].append("[CANCEL] Download cancelled by user.")
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "No active download"})

@app.route('/api/open_folder', methods=['POST'])
def open_folder():
    path = STATE["save_path"]
    try:
        os.startfile(path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/play_file', methods=['POST'])
def play_file():
    # Opens in system default player
    data = request.json
    filename = data.get('filename', '')
    # Normalize path separators
    filename = os.path.normpath(filename)
    if not filename or not os.path.exists(filename):
        return jsonify({"success": False, "error": "File not found"})
    try:
        os.startfile(filename)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})



APP_VERSION = "2.1.0"
GITHUB_REPO = "elchanany/atomic-downloader"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

@app.route('/api/connectivity', methods=['GET'])
def check_connectivity():
    """Quick internet connectivity check."""
    import requests as req
    try:
        req.get("https://www.google.com", timeout=3)
        return jsonify({"online": True})
    except:
        return jsonify({"online": False})

@app.route('/api/check_updates', methods=['GET'])
def check_updates():
    """Check for yt-dlp updates (PyPI) and app updates (GitHub releases)."""
    import requests as req
    result = {
        "app_version": APP_VERSION,
        "app_latest": APP_VERSION,
        "app_update": False,
        "app_download_url": "",
        "ytdlp_current": "",
        "ytdlp_latest": "",
        "ytdlp_update": False,
        "online": True
    }
    
    # Current yt-dlp version
    try:
        import yt_dlp
        result["ytdlp_current"] = yt_dlp.version.__version__
    except:
        result["ytdlp_current"] = "unknown"
    
    # Check yt-dlp latest from PyPI
    try:
        resp = req.get("https://pypi.org/pypi/yt-dlp/json", timeout=5)
        if resp.ok:
            data = resp.json()
            latest = data.get("info", {}).get("version", "")
            result["ytdlp_latest"] = latest
            if latest and result["ytdlp_current"] != "unknown":
                result["ytdlp_update"] = latest != result["ytdlp_current"]
    except:
        result["online"] = False
    
    # Check app latest from GitHub releases
    try:
        resp = req.get(GITHUB_API, timeout=5, headers={"Accept": "application/vnd.github.v3+json"})
        if resp.ok:
            data = resp.json()
            tag = data.get("tag_name", "")
            # Remove 'v' prefix if present (e.g., "v2.2.0" -> "2.2.0")
            latest_version = tag.lstrip("v")
            result["app_latest"] = latest_version
            
            # Compare versions
            try:
                from packaging.version import Version
                result["app_update"] = Version(latest_version) > Version(APP_VERSION)
            except:
                result["app_update"] = latest_version != APP_VERSION
            
            # Get download URL (zip of source code)
            result["app_download_url"] = data.get("zipball_url", "")
    except:
        pass
    
    return jsonify(result)

@app.route('/api/update_ytdlp', methods=['POST'])
def update_ytdlp():
    """Update yt-dlp via pip."""
    import subprocess
    try:
        r = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode == 0:
            return jsonify({"success": True, "output": r.stdout[-500:]})
        else:
            return jsonify({"success": False, "error": r.stderr[-500:]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/update_app', methods=['POST'])
def update_app():
    """Download latest release from GitHub and apply update."""
    import requests as req
    import zipfile
    import tempfile
    import shutil
    
    try:
        # Get latest release info
        resp = req.get(GITHUB_API, timeout=10, headers={"Accept": "application/vnd.github.v3+json"})
        if not resp.ok:
            return jsonify({"success": False, "error": "Cannot reach GitHub"})
        
        data = resp.json()
        zip_url = data.get("zipball_url", "")
        if not zip_url:
            return jsonify({"success": False, "error": "No download URL found"})
        
        # Download the zip
        STATE["logs"].append("[UPDATE] Downloading latest version from GitHub...")
        zip_resp = req.get(zip_url, timeout=60, stream=True)
        if not zip_resp.ok:
            return jsonify({"success": False, "error": "Failed to download update"})
        
        # Save to temp file
        tmp_zip = os.path.join(tempfile.gettempdir(), "atomic_update.zip")
        with open(tmp_zip, 'wb') as f:
            for chunk in zip_resp.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract and apply
        STATE["logs"].append("[UPDATE] Extracting update...")
        tmp_dir = os.path.join(tempfile.gettempdir(), "atomic_update_extract")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        
        with zipfile.ZipFile(tmp_zip, 'r') as z:
            z.extractall(tmp_dir)
        
        # GitHub zipball extracts to a folder like "user-repo-hash/"
        extracted_dirs = [d for d in os.listdir(tmp_dir) if os.path.isdir(os.path.join(tmp_dir, d))]
        if not extracted_dirs:
            return jsonify({"success": False, "error": "Invalid archive structure"})
        
        source_dir = os.path.join(tmp_dir, extracted_dirs[0])
        app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Copy updated files (skip .venv, .git, __pycache__, cookies.txt)
        skip = {'.venv', '.git', '__pycache__', 'cookies.txt', '.gitignore'}
        updated_files = []
        for item in os.listdir(source_dir):
            if item in skip:
                continue
            src = os.path.join(source_dir, item)
            dst = os.path.join(app_dir, item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            updated_files.append(item)
        
        # Cleanup
        os.remove(tmp_zip)
        shutil.rmtree(tmp_dir)
        
        STATE["logs"].append(f"[UPDATE] Updated {len(updated_files)} files. Restart the app to apply changes.")
        
        return jsonify({
            "success": True, 
            "message": f"Updated {len(updated_files)} files. Please restart the app.",
            "updated_files": updated_files
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    print("Starting Web GUI...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, use_reloader=False)
