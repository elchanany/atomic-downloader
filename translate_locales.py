"""
Auto-translate all locale files from English using deep-translator (Google Translate).
Run: pip install deep-translator && python translate_locales.py
"""
import json
import os
import time

try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("ERROR: deep-translator not installed.")
    print("Run: pip install deep-translator")
    exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, 'static', 'locales')

# Map locale code to Google Translate language code
LANG_MAP = {
    "es": "es", "fr": "fr", "de": "de", "ru": "ru", "ar": "ar",
    "zh-CN": "zh-CN", "zh-TW": "zh-TW", "ja": "ja", "ko": "ko",
    "pt": "pt", "it": "it", "nl": "nl", "tr": "tr", "pl": "pl",
    "id": "id", "hi": "hi", "vi": "vi", "th": "th", "sv": "sv",
    "da": "da", "no": "no", "fi": "fi", "el": "el", "cs": "cs",
    "hu": "hu", "ro": "ro", "uk": "uk", "bg": "bg", "hr": "hr",
    "sr": "sr", "sk": "sk", "ca": "ca", "tl": "tl", "ms": "ms",
    "fa": "fa", "sw": "sw", "ta": "ta", "te": "te", "ur": "ur",
    "bn": "bn", "mr": "mr", "gu": "gu", "pa": "pa", "kn": "kn",
    "ml": "ml",
}

# Keys that should NOT be translated (technical values, brand names)
SKIP_KEYS = {"_meta", "title"}  # _meta is metadata, title is "ATOMIC"
SKIP_VALUES = {"ATOMIC", "DOWNLOADER", "SponsorBlock", "HTTP/SOCKS5 proxy URL",
               "MP3", "AAC", "FLAC", "M4A", "Opus", "WAV", "Vorbis",
               "MP4", "MKV", "WebM", "Chrome", "Edge", "Firefox", "Brave",
               "Opera", "Vivaldi", "yt-dlp", "GitHub Repository", "kbps",
               "ASCII"}


def translate_value(translator, value):
    """Translate a single string value."""
    if not value or not isinstance(value, str):
        return value
    
    # Skip technical/brand values
    stripped = value.strip()
    if stripped in SKIP_VALUES:
        return value
    
    # Skip values that are mostly technical (contain {placeholders})
    # But translate the text around them
    if '{' in value:
        # Translate anyway, placeholders usually survive
        pass
    
    try:
        translated = translator.translate(value)
        return translated if translated else value
    except Exception as e:
        print(f"    Warning: Could not translate '{value[:40]}...': {e}")
        return value


def translate_dict(translator, data, parent_key=""):
    """Recursively translate all string values in a dict."""
    result = {}
    for key, value in data.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        
        # Skip _meta section
        if key == "_meta":
            result[key] = value
            continue
        
        if isinstance(value, dict):
            result[key] = translate_dict(translator, value, full_key)
        elif isinstance(value, str):
            result[key] = translate_value(translator, value)
        else:
            result[key] = value
    
    return result


def main():
    # Load English source
    en_path = os.path.join(LOCALES_DIR, 'en.json')
    with open(en_path, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    total = len(LANG_MAP)
    done = 0
    
    for locale_code, google_code in LANG_MAP.items():
        done += 1
        out_path = os.path.join(LOCALES_DIR, f'{locale_code}.json')
        
        # Read existing file to preserve _meta
        existing_meta = None
        if os.path.exists(out_path):
            with open(out_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                existing_meta = existing.get('_meta')
        
        print(f"[{done}/{total}] Translating to {locale_code} ({google_code})...")
        
        try:
            translator = GoogleTranslator(source='en', target=google_code)
            translated = translate_dict(translator, en_data)
            
            # Restore original _meta
            if existing_meta:
                translated['_meta'] = existing_meta
            
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(translated, f, indent=4, ensure_ascii=False)
            
            print(f"    OK: {locale_code}.json saved")
            
            # Small delay to be nice to Google
            time.sleep(0.3)
            
        except Exception as e:
            print(f"    ERROR: {locale_code} failed: {e}")
            continue

    print(f"\nDone! Translated {done} locale files.")


if __name__ == '__main__':
    main()
