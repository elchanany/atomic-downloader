<p align="center">
  <img src="static/images/logo.png" alt="Atomic Downloader" width="120" height="120" style="border-radius: 20px;">
</p>

<h1 align="center">⚡ Atomic Downloader</h1>

<p align="center">
  <strong>A sleek, modern video & audio downloader with a cyberpunk-inspired UI</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1.0-00f3ff?style=for-the-badge&labelColor=0a0a0f" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-3776ab?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0f" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows-0078d4?style=for-the-badge&logo=windows&logoColor=white&labelColor=0a0a0f" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge&labelColor=0a0a0f" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/languages-47-ff6b6b?style=flat-square&labelColor=0a0a0f" alt="Languages">
  <img src="https://img.shields.io/badge/sites-1000+-ff9f43?style=flat-square&labelColor=0a0a0f" alt="Supported Sites">
</p>

---

## ✨ Features

- 🎬 **Download Videos & Audio** — From YouTube, Instagram, TikTok, Twitter/X, and 1000+ sites
- 🎵 **Audio Extraction** — One-click MP3 conversion with quality selection
- 🌍 **47 Languages** — Full localization with RTL support (Hebrew, Arabic, etc.)
- 🎨 **Cyberpunk UI** — Neon-glow design with smooth animations and dark theme
- 📊 **Real-time Progress** — Speed, ETA, and file size display with analog progress bar
- 📋 **Download History** — Browse, play, and manage past downloads
- 🔄 **Auto-Updates** — Built-in update checker for both the app and yt-dlp engine
- 🔐 **Smart Login** — Cookie-based authentication for restricted content
- ⚙️ **Advanced Settings** — Proxy, rate limiting, SponsorBlock, subtitles, and more
- 🌐 **Offline Ready** — App loads fully offline, shows clear indicator when no internet

## 🚀 Quick Start

### Option 1: Run from Source

```bash
# Clone the repository
git clone https://github.com/elchanany/atomic-downloader.git
cd atomic-downloader

# Run the launcher (handles everything automatically)
python launcher.py
```

The launcher will:
1. Create a virtual environment
2. Install all dependencies
3. Show a first-run setup UI
4. Launch the app

### Option 2: Windows EXE

Download the latest `AtomicDownloader.exe` from [Releases](https://github.com/elchanany/atomic-downloader/releases).

> **Note:** [FFmpeg](https://ffmpeg.org/download.html) must be installed and available in your system PATH.

## 🛠️ Building from Source

```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
build\build.bat
```

Output: `dist/AtomicDownloader.exe`

## 📦 Requirements

| Dependency | Purpose |
|---|---|
| Python 3.8+ | Runtime |
| FFmpeg | Audio/video processing |
| yt-dlp | Download engine |
| Flask | Web backend |
| pywebview | Desktop window |

All Python dependencies are auto-installed by the launcher.

## 🌐 Supported Languages

Arabic, Bengali, Bulgarian, Catalan, Chinese (Simplified & Traditional), Croatian, Czech, Danish, Dutch, English, Finnish, French, German, Greek, Gujarati, Hebrew, Hindi, Hungarian, Indonesian, Italian, Japanese, Kannada, Korean, Malayalam, Marathi, Malay, Norwegian, Panjabi, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Spanish, Swahili, Swedish, Tamil, Telugu, Thai, Turkish, Ukrainian, Urdu, Vietnamese, Filipino

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/elchanany">elchanany</a>
</p>
