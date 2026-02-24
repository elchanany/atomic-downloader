import yt_dlp
import os
import threading
import shutil
import glob
from utils import is_pornhub, is_tiktok

import re

def find_ffmpeg():
    """Check if ffmpeg is available. Returns path or None."""
    # 1. Check in project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    local_ffmpeg = os.path.join(project_dir, 'ffmpeg.exe')
    if os.path.exists(local_ffmpeg):
        return project_dir
    
    # 2. Check system PATH (current process)
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        return os.path.dirname(system_ffmpeg)
    
    # 3. Refresh PATH from Windows registry and re-check
    try:
        import winreg
        # Read user PATH
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment') as key:
            user_path = winreg.QueryValueEx(key, 'Path')[0]
        # Read system PATH
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
            sys_path = winreg.QueryValueEx(key, 'Path')[0]
        
        fresh_path = user_path + ';' + sys_path
        for p in fresh_path.split(';'):
            p = p.strip()
            if p and os.path.exists(os.path.join(p, 'ffmpeg.exe')):
                return p
    except Exception:
        pass
    
    # 4. Search winget package directories
    local_appdata = os.environ.get('LOCALAPPDATA', '')
    if local_appdata:
        winget_pattern = os.path.join(local_appdata, 'Microsoft', 'WinGet', 'Packages', '*FFmpeg*', '**', 'bin')
        for bin_dir in glob.glob(winget_pattern, recursive=True):
            if os.path.exists(os.path.join(bin_dir, 'ffmpeg.exe')):
                return bin_dir
    
    # 5. Check common install locations
    common_paths = [
        r'C:\ffmpeg\bin',
        r'C:\Program Files\ffmpeg\bin',
        r'C:\Program Files (x86)\ffmpeg\bin',
    ]
    for p in common_paths:
        if os.path.exists(os.path.join(p, 'ffmpeg.exe')):
            return p
    
    return None

class MyLogger:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def _clean_msg(self, msg):
        return self.ansi_escape.sub('', msg)

    def debug(self, msg):
        if msg.startswith('[debug] '):
            return
        clean = self._clean_msg(msg)
        if "[download]" in clean and ("%" in clean or "frag" in clean):
            return
        self.log_callback(clean)

    def info(self, msg):
        clean = self._clean_msg(msg)
        if "[download]" in clean and ("%" in clean or "frag" in clean or "ETA" in clean):
            return
        self.log_callback(clean)

    def warning(self, msg):
        self.log_callback(f"WARNING: {self._clean_msg(msg)}")

    def error(self, msg):
        self.log_callback(f"ERROR: {self._clean_msg(msg)}")

class Downloader:
    def __init__(self):
        self.cancel_requested = False
        self._download_stream_count = 1
        self._current_stream = 0

    def get_ph_options(self, cookies_path):
        return {
            'cookiefile': cookies_path,
            'nocheckcertificate': True,
            'legacy_server_connect': True,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 5,
            'http_headers': {
                'Referer': 'https://www.pornhub.com/',
                'Origin': 'https://www.pornhub.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'concurrent_fragment_downloads': 4,
        }

    def get_tiktok_options(self):
        return {
            'nocheckcertificate': True,
            'legacy_server_connect': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            },
        }

    def get_quality_opts(self, quality, ffmpeg_path):
        has_ffmpeg = ffmpeg_path is not None
        
        # Base options to prefer better video streams
        # Prefer higher bitrate and standard codecs
        opts = {
            'format_sort': ['res', 'fps', 'tbr', 'vcodec:h264', 'acodec:aac'],
            'merge_output_format': 'mp4'
        }
        
        if not has_ffmpeg:
            # Fallback for no ffmpeg
            if quality == 'audio':
                return {'format': 'bestaudio/best'}
            elif quality in ['4k', '1080p', '720p', '480p', '360p']:
                h = int(quality.replace('p', '').replace('4k', '2160'))
                return {'format': f'best[height<={h}]/best'}
            else:
                return {'format': 'best'}
        
        # With FFmpeg: split streams for max quality
        if quality == 'audio':
            return {
                'format': 'bestaudio/best', 
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }
            
        # Video Quality Logic
        # We use a localized format string that attempts to get the best video 
        # that fits the constraint, falling back to 'best' if needed.
        if quality in ['4k', '1080p', '720p', '480p', '360p']:
             h = int(quality.replace('p', '').replace('4k', '2160'))
             opts['format'] = f'bestvideo[height<={h}]+bestaudio/best[height<={h}]/best'
        else:
             # Best / Max
             opts['format'] = 'bestvideo+bestaudio/best'
             
        return opts

    def probe_formats(self, url):
        """Extract available video qualities from a URL without downloading."""
        try:
            opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            ffmpeg_path = find_ffmpeg()
            if ffmpeg_path:
                opts['ffmpeg_location'] = ffmpeg_path
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return []
                
                formats = info.get('formats', [])
                
                # Collect unique heights
                heights = set()
                for f in formats:
                    h = f.get('height')
                    if h and isinstance(h, int) and h > 0:
                        heights.add(h)
                
                # Map to standard quality labels
                quality_map = []
                standard_heights = [2160, 1080, 720, 480, 360]
                
                for sh in standard_heights:
                    matching = [h for h in heights if abs(h - sh) <= 20]
                    if matching:
                        label_map = {2160: '4K', 1080: '1080p', 720: '720p', 480: '480p', 360: '360p'}
                        actual_h = max(matching)
                        quality_map.append({
                            'value': label_map.get(sh, f'{sh}p').lower().replace(' ', ''),
                            'label': f'{label_map.get(sh, str(sh)+"p")} ({actual_h}p)',
                            'height': actual_h
                        })
                
                quality_map.append({'value': 'audio', 'label': '🎵 Audio Only', 'height': 0})
                
                return quality_map
                
        except Exception as e:
            return []

    def _apply_advanced_opts(self, opts, advanced, save_path, quality):
        """Apply advanced settings dict to yt-dlp options."""
        if not advanced:
            return opts

        # --- Download ---
        concurrent = advanced.get('concurrent', 1)
        if concurrent > 1:
            opts['concurrent_fragment_downloads'] = concurrent

        ratelimit = advanced.get('ratelimit', 0)
        if ratelimit > 0:
            opts['ratelimit'] = ratelimit * 1024  # KB/s -> B/s

        retries = advanced.get('retries', 10)
        opts['retries'] = retries

        chunksize = advanced.get('chunksize', 0)
        if chunksize > 0:
            opts['http_chunk_size'] = chunksize * 1024 * 1024  # MB -> bytes

        # --- Format / Audio ---
        audio_format = advanced.get('audioFormat', 'mp3')
        audio_quality = advanced.get('audioQuality', '192')
        container = advanced.get('container', 'mp4')

        if quality == 'audio':
            # Override audio extraction settings
            opts['postprocessors'] = opts.get('postprocessors', [])
            # Remove existing audio PP if any, we'll add our own
            opts['postprocessors'] = [
                pp for pp in opts['postprocessors']
                if pp.get('key') != 'FFmpegExtractAudio'
            ]
            opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': audio_quality,
            })
        else:
            # Set merge output format
            if container:
                opts['merge_output_format'] = container

        # --- Content: Subtitles ---
        if advanced.get('subtitles'):
            opts['writesubtitles'] = True
            opts['writeautomaticsub'] = True
            sub_langs = advanced.get('subLangs', 'he,en')
            opts['subtitleslangs'] = [lang.strip() for lang in sub_langs.split(',')]
            opts['postprocessors'] = opts.get('postprocessors', [])
            opts['postprocessors'].append({'key': 'FFmpegEmbedSubtitle'})

        # --- Content: Thumbnail ---
        if advanced.get('embedThumb'):
            opts['writethumbnail'] = True
            opts['postprocessors'] = opts.get('postprocessors', [])
            opts['postprocessors'].append({'key': 'EmbedThumbnail'})

        # --- Content: Metadata ---
        if advanced.get('embedMetadata'):
            opts['postprocessors'] = opts.get('postprocessors', [])
            opts['postprocessors'].append({'key': 'FFmpegMetadata', 'add_chapters': True})

        # --- Content: SponsorBlock ---
        if advanced.get('sponsorblock'):
            sb_action = advanced.get('sbAction', 'mark')
            cats = ['sponsor', 'selfpromo', 'interaction', 'intro', 'outro']
            if sb_action == 'remove':
                opts['sponsorblock_remove'] = cats
            else:
                opts['sponsorblock_mark'] = cats
            opts['postprocessors'] = opts.get('postprocessors', [])
            opts['postprocessors'].append({
                'key': 'SponsorBlock',
                'categories': cats,
            })
            opts['postprocessors'].append({
                'key': 'ModifyChapters',
                'remove_sponsor_segments': cats if sb_action == 'remove' else [],
            })

        # --- Network ---
        proxy = advanced.get('proxy', '')
        if proxy:
            opts['proxy'] = proxy

        if advanced.get('impersonate'):
            opts['nocheckcertificate'] = True
            opts['legacy_server_connect'] = True

        sleep_interval = advanced.get('sleep', 0)
        if sleep_interval > 0:
            opts['sleep_interval'] = sleep_interval

        if advanced.get('noCheckCert'):
            opts['nocheckcertificate'] = True

        # --- Filesystem ---
        if advanced.get('archive'):
            opts['download_archive'] = os.path.join(save_path, '.download_archive.txt')

        if advanced.get('restrictFn'):
            opts['restrictfilenames'] = True

        if advanced.get('noOverwrites'):
            opts['nooverwrites'] = True

        if advanced.get('noPlaylist'):
            opts['noplaylist'] = True

        outtmpl = advanced.get('outtmpl', '')
        if outtmpl:
            opts['outtmpl'] = os.path.join(save_path, outtmpl)

        # --- Cookies from Browser ---
        cookies_browser = advanced.get('cookiesBrowser', '')
        if cookies_browser:
            opts['cookiesfrombrowser'] = (cookies_browser,)

        return opts
    
    def download(self, urls, save_path, cookies_path, quality, advanced=None, progress_callback=None, log_callback=None, finished_callback=None, error_callback=None):
        def run():
            self.cancel_requested = False
            target_urls = urls if isinstance(urls, list) else [urls]
            
            # Re-check FFmpeg at download time
            ffmpeg_path = find_ffmpeg()
            
            if ffmpeg_path:
                log_callback(f"[OK] FFmpeg found: {ffmpeg_path}")
            else:
                log_callback("[WARN] FFmpeg not found - using single stream mode (lower quality)")

            common_opts = {
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'logger': MyLogger(log_callback),
                'progress_hooks': [lambda d: self._progress_hook(d, progress_callback)],
                'socket_timeout': 30,
                'retries': 10,
                'fragment_retries': 10,
                'extractor_retries': 3,
                'noplaylist': True, # Default to single video
                'nocolor': True, # Disable ANSI colors in output
                'extractor_args': {'generic': {'impersonate': ['true']}}, # Bypass Cloudflare
            }
            
            if ffmpeg_path:
                common_opts['ffmpeg_location'] = ffmpeg_path
            
            quality_opts = self.get_quality_opts(quality, ffmpeg_path)
            common_opts.update(quality_opts)

            # Apply advanced settings
            if advanced:
                common_opts = self._apply_advanced_opts(common_opts, advanced, save_path, quality)
                if advanced.get('concurrent', 1) > 1:
                    log_callback(f"[ADV] Concurrent fragments: {advanced['concurrent']}")
                if advanced.get('proxy'):
                    log_callback(f"[ADV] Proxy: {advanced['proxy']}")
                if advanced.get('impersonate'):
                    log_callback("[ADV] Client impersonation: Chrome")
                if advanced.get('subtitles'):
                    log_callback(f"[ADV] Subtitles: {advanced.get('subLangs', 'he,en')}")
                if advanced.get('sponsorblock'):
                    log_callback(f"[ADV] SponsorBlock: {advanced.get('sbAction', 'mark')}")
            
            # Detect if we're doing split streams (video+audio)
            fmt = quality_opts.get('format', '')
            self._download_stream_count = 2 if '+' in fmt else 1
            self._current_stream = 0

            target_urls = [u.strip() for u in target_urls if u.strip()]
            total_items = len(target_urls)
            
            for index, url in enumerate(target_urls):
                if self.cancel_requested:
                    log_callback("[CANCEL] Download cancelled.")
                    return
                log_callback(f">> Processing {index+1}/{total_items}: {url}")
                self._current_stream = 0  # Reset per URL
                
                current_opts = common_opts.copy()
                
                if is_pornhub(url):
                    log_callback("[STEALTH] Pornhub detected: Activating Stealth Mode")
                    if not cookies_path or not os.path.exists(cookies_path):
                        error_callback("Missing Cookies! Pornhub requires login.")
                        return
                    ph_opts = self.get_ph_options(cookies_path)
                    current_opts.update(ph_opts)
                elif is_tiktok(url):
                    log_callback("[SITE] TikTok detected: Applying TikTok options")
                    tt_opts = self.get_tiktok_options()
                    current_opts.update(tt_opts)

                try:
                    with yt_dlp.YoutubeDL(current_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        
                        filename = ydl.prepare_filename(info)
                        if quality == 'audio':
                             # FFmpegExtractAudio converts to .mp3
                             filename = os.path.splitext(filename)[0] + '.mp3'
                        elif not filename.endswith('.mp4'):
                             filename = os.path.splitext(filename)[0] + '.mp4'
                        
                        title = info.get('title', 'Unknown Video')
                        thumbnail = info.get('thumbnail', None)
                        
                        finished_callback({
                            "url": url,
                            "title": title,
                            "filename": filename,
                            "thumbnail": thumbnail,
                            "index": index,
                            "total": total_items
                        })

                except Exception as e:
                    err_str = str(e)
                    
                    # SSL error auto-retry
                    if "SSL" in err_str or "UNEXPECTED_EOF" in err_str or "ssl" in err_str.lower():
                        log_callback("[RETRY] SSL error detected - retrying without certificate verification...")
                        retry_opts = current_opts.copy()
                        retry_opts['nocheckcertificate'] = True
                        retry_opts['legacy_server_connect'] = True
                        try:
                            with yt_dlp.YoutubeDL(retry_opts) as ydl:
                                info = ydl.extract_info(url, download=True)
                                filename = ydl.prepare_filename(info)
                                if quality == 'audio':
                                    filename = os.path.splitext(filename)[0] + '.mp3'
                                elif not filename.endswith('.mp4'):
                                    filename = os.path.splitext(filename)[0] + '.mp4'
                                title = info.get('title', 'Unknown Video')
                                thumbnail = info.get('thumbnail', None)
                                finished_callback({
                                    "url": url,
                                    "title": title,
                                    "filename": filename,
                                    "thumbnail": thumbnail,
                                    "index": index,
                                    "total": total_items
                                })
                            continue
                        except Exception as e2:
                            err_str = str(e2)
                            error_message = f"[ERR] SSL retry also failed: {err_str}"
                            error_callback(f"{url}: {error_message}")
                            continue
                    
                    if "getaddrinfo failed" in err_str or "Network is unreachable" in err_str:
                        error_message = "[ERR] No Internet Connection (DNS/Network Error)"
                    elif "Video unavailable" in err_str:
                         error_message = "[ERR] Video Not Found / Deleted"
                    elif "Private video" in err_str:
                         error_message = "[ERR] Private Video (Login Required)"
                    elif "ffmpeg" in err_str.lower():
                         error_message = "[ERR] FFmpeg Error - try restarting the app"
                    else:
                        error_message = f"Error: {err_str}"
                    
                    error_callback(f"{url}: {error_message}")
                    continue
            
            log_callback("[DONE] Batch Job Complete")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def _progress_hook(self, d, callback):
        if self.cancel_requested:
            raise Exception("Download cancelled by user")
        
        status_data = {
            'status': d.get('status'),
            'percent': 0,
            'speed': '0',
            'eta': '--',
            'eta_seconds': None,
            'total': '0',
            'playlist_index': d.get('playlist_index'),
            'playlist_count': d.get('playlist_count') or d.get('n_entries'),
            'title': d.get('info_dict', {}).get('title', '') if isinstance(d.get('info_dict'), dict) else ''
        }

        if d['status'] == 'downloading':
            try:
                # Calculate raw percent from actual bytes
                downloaded = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                if total_bytes and total_bytes > 0:
                    raw_percent = downloaded / total_bytes
                else:
                    # Fallback: try _percent_str
                    p = d.get('_percent_str', '0%').replace('%','').strip()
                    raw_percent = float(p) / 100
            except:
                try:
                    current_frag = d.get('fragment_index', 0)
                    total_frags = d.get('fragment_count', 0)
                    if current_frag and total_frags:
                         raw_percent = float(current_frag) / float(total_frags)
                    else:
                         raw_percent = 0
                except:
                    raw_percent = 0
            
            # Adjust for multi-stream (video + audio = 2 streams)
            if self._download_stream_count > 1:
                stream_weight = 1.0 / self._download_stream_count
                # Cap raw_percent at 1.0 just in case
                raw_percent = min(1.0, max(0.0, raw_percent))
                percent = (self._current_stream * stream_weight) + (raw_percent * stream_weight)
            else:
                percent = raw_percent
            
            status_data['percent'] = min(1.0, percent)
            status_data['speed'] = d.get('_speed_str', '--')
            status_data['total'] = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str', '--')
            
            # ETA: try multiple methods to get a valid ETA
            try:
                raw_eta = d.get('eta')  # can be int, float, or None
                
                # Convert to int if present
                if raw_eta is not None:
                    raw_eta = int(raw_eta)
                
                # Method 1: yt-dlp provides eta directly
                if not raw_eta or raw_eta <= 0:
                    # Method 2: Calculate from speed + remaining bytes
                    speed_bps = d.get('speed')
                    downloaded = d.get('downloaded_bytes', 0)
                    total_b = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    if speed_bps and speed_bps > 0 and total_b and total_b > downloaded:
                        raw_eta = int((total_b - downloaded) / speed_bps)
                
                if not raw_eta or raw_eta <= 0:
                    # Method 3: Fragment-based estimation (for HLS/DASH)
                    frag_idx = d.get('fragment_index', 0)
                    frag_count = d.get('fragment_count', 0)
                    elapsed = d.get('elapsed', 0)
                    if frag_idx and frag_idx > 0 and frag_count and frag_count > frag_idx and elapsed and elapsed > 0:
                        time_per_frag = elapsed / frag_idx
                        remaining_frags = frag_count - frag_idx
                        raw_eta = int(remaining_frags * time_per_frag)
                
                if raw_eta and raw_eta > 0:
                    status_data['eta_seconds'] = raw_eta
                    h = int(raw_eta // 3600)
                    m = int((raw_eta % 3600) // 60)
                    s = int(raw_eta % 60)
                    if h > 0:
                        status_data['eta'] = f'{h}:{m:02d}:{s:02d}'
                    else:
                        status_data['eta'] = f'{m:02d}:{s:02d}'
                else:
                    status_data['eta_seconds'] = None
                    status_data['eta'] = '--'
            except Exception:
                status_data['eta_seconds'] = None
                status_data['eta'] = '--'


        elif d['status'] == 'finished':
            # A stream finished downloading
            if self._download_stream_count > 1:
                 self._current_stream += 1
            
            # Only mark as 100% "processing" if this was the last stream or single stream
            if self._current_stream >= self._download_stream_count:
                status_data['status'] = 'processing'
                status_data['percent'] = 1.0
                status_data['eta'] = '--'
            else:
                # Just an intermediate finish (e.g. video done, starting audio)
                # Don't send 'processing' yet, just keep it as 'downloading' effectively
                # or send a special status update?
                # Actually, the next hook call will be 'downloading' for the next stream.
                return # Skip callback for intermediate finish to avoid jumping to 100% then back
                
        if callback:
             callback(status_data)
