import json
import os
import shutil

LANGUAGES = [
    {"code": "en", "name": "English", "dir": "ltr"},
    {"code": "he", "name": "עברית", "dir": "rtl"},
    {"code": "es", "name": "Español", "dir": "ltr"},
    {"code": "fr", "name": "Français", "dir": "ltr"},
    {"code": "de", "name": "Deutsch", "dir": "ltr"},
    {"code": "ru", "name": "Русский", "dir": "ltr"},
    {"code": "ar", "name": "العربية", "dir": "rtl"},
    {"code": "zh-CN", "name": "简体中文", "dir": "ltr"},
    {"code": "zh-TW", "name": "繁體中文", "dir": "ltr"},
    {"code": "ja", "name": "日本語", "dir": "ltr"},
    {"code": "ko", "name": "한국어", "dir": "ltr"},
    {"code": "pt", "name": "Português", "dir": "ltr"},
    {"code": "it", "name": "Italiano", "dir": "ltr"},
    {"code": "nl", "name": "Nederlands", "dir": "ltr"},
    {"code": "tr", "name": "Türkçe", "dir": "ltr"},
    {"code": "pl", "name": "Polski", "dir": "ltr"},
    {"code": "id", "name": "Bahasa Indonesia", "dir": "ltr"},
    {"code": "hi", "name": "हिन्दी", "dir": "ltr"},
    {"code": "vi", "name": "Tiếng Việt", "dir": "ltr"},
    {"code": "th", "name": "ไทย", "dir": "ltr"},
    {"code": "sv", "name": "Svenska", "dir": "ltr"},
    {"code": "da", "name": "Dansk", "dir": "ltr"},
    {"code": "no", "name": "Norsk", "dir": "ltr"},
    {"code": "fi", "name": "Suomi", "dir": "ltr"},
    {"code": "el", "name": "Ελληνικά", "dir": "ltr"},
    {"code": "cs", "name": "Čeština", "dir": "ltr"},
    {"code": "hu", "name": "Magyar", "dir": "ltr"},
    {"code": "ro", "name": "Română", "dir": "ltr"},
    {"code": "uk", "name": "Українська", "dir": "ltr"},
    {"code": "bg", "name": "Български", "dir": "ltr"},
    {"code": "hr", "name": "Hrvatski", "dir": "ltr"},
    {"code": "sr", "name": "Српски", "dir": "ltr"},
    {"code": "sk", "name": "Slovenčina", "dir": "ltr"},
    {"code": "ca", "name": "Català", "dir": "ltr"},
    {"code": "tl", "name": "Filipino", "dir": "ltr"},
    {"code": "ms", "name": "Bahasa Melayu", "dir": "ltr"},
    {"code": "fa", "name": "فارسی", "dir": "rtl"},
    {"code": "sw", "name": "Kiswahili", "dir": "ltr"},
    {"code": "ta", "name": "தமிழ்", "dir": "ltr"},
    {"code": "te", "name": "తెలుగు", "dir": "ltr"},
    {"code": "ur", "name": "اردو", "dir": "rtl"},
    {"code": "bn", "name": "বাংলা", "dir": "ltr"},
    {"code": "mr", "name": "मराठी", "dir": "ltr"},
    {"code": "gu", "name": "ગુજરાતી", "dir": "ltr"},
    {"code": "pa", "name": "ਪੰਜਾਬੀ", "dir": "ltr"},
    {"code": "kn", "name": "ಕನ್ನಡ", "dir": "ltr"},
    {"code": "ml", "name": "മലയാളം", "dir": "ltr"}
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, 'static', 'locales')

def main():
    if not os.path.exists(LOCALES_DIR):
        os.makedirs(LOCALES_DIR)

    # Read base English file
    with open(os.path.join(LOCALES_DIR, 'en.json'), 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    generated = 0
    for lang in LANGUAGES:
        code = lang['code']
        path = os.path.join(LOCALES_DIR, f"{code}.json")
        
        if code == 'en' or code == 'he':
            continue  # Skip existing manually created ones
            
        # Copy English data but update _meta with this language's info
        lang_data = json.loads(json.dumps(en_data))  # deep copy
        lang_data['_meta'] = {
            'displayName': lang['name'],
            'dir': lang['dir']
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, indent=4, ensure_ascii=False)
        
        generated += 1
        print(f"Generated {code}.json ({lang['name']})")

    print(f"\nDone! Generated {generated} locale files.")

if __name__ == '__main__':
    main()
