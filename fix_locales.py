"""
Fix: 
1. Rename dashboard.stats.eta to "Time Left" in all locales
2. Add dashboard.no_internet key to all locales
"""
import json
import os

LOCALES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'locales')

TIME_LEFT_TRANSLATIONS = {
    "en": "Time Left", "he": "זמן נותר", "es": "Tiempo restante",
    "fr": "Temps restant", "de": "Verbleibende Zeit", "ru": "Оставшееся время",
    "ar": "الوقت المتبقي", "zh-CN": "剩余时间", "zh-TW": "剩餘時間",
    "ja": "残り時間", "ko": "남은 시간", "pt": "Tempo restante",
    "it": "Tempo rimanente", "nl": "Resterende tijd", "tr": "Kalan süre",
    "pl": "Pozostały czas", "id": "Waktu tersisa", "hi": "शेष समय",
    "vi": "Thời gian còn lại", "th": "เวลาที่เหลือ", "sv": "Återstående tid",
    "da": "Resterende tid", "no": "Gjenstående tid", "fi": "Jäljellä oleva aika",
    "el": "Υπολειπόμενος χρόνος", "cs": "Zbývající čas", "hu": "Hátralévő idő",
    "ro": "Timp rămas", "uk": "Час, що залишився", "bg": "Оставащо време",
    "hr": "Preostalo vrijeme", "sr": "Преостало време", "sk": "Zostávajúci čas",
    "ca": "Temps restant", "tl": "Natitirang oras", "ms": "Masa yang tinggal",
    "fa": "زمان باقی‌مانده", "sw": "Muda uliobaki", "ta": "மீதமுள்ள நேரம்",
    "te": "మిగిలిన సమయం", "ur": "باقی وقت", "bn": "বাকি সময়",
    "mr": "उरलेला वेळ", "gu": "બાકીનો સમય", "pa": "ਬਾਕੀ ਸਮਾਂ",
    "kn": "ಉಳಿದ ಸಮಯ", "ml": "ശേഷിക്കുന്ന സമയം", "am": "የቀረ ጊዜ",
}

NO_INTERNET_TRANSLATIONS = {
    "en": "No Internet Connection", "he": "אין חיבור לאינטרנט", 
    "es": "Sin conexión a Internet", "fr": "Pas de connexion Internet",
    "de": "Keine Internetverbindung", "ru": "Нет подключения к интернету",
    "ar": "لا يوجد اتصال بالإنترنت", "zh-CN": "没有互联网连接", "zh-TW": "沒有網路連線",
    "ja": "インターネット接続なし", "ko": "인터넷 연결 없음", "pt": "Sem conexão com a Internet",
    "it": "Nessuna connessione Internet", "nl": "Geen internetverbinding",
    "tr": "İnternet bağlantısı yok", "pl": "Brak połączenia z internetem",
    "id": "Tidak ada koneksi internet", "hi": "इंटरनेट कनेक्शन नहीं है",
    "vi": "Không có kết nối Internet", "th": "ไม่มีการเชื่อมต่ออินเทอร์เน็ต",
    "sv": "Ingen internetanslutning", "da": "Ingen internetforbindelse",
    "no": "Ingen internettilkobling", "fi": "Ei internet-yhteyttä",
    "el": "Δεν υπάρχει σύνδεση στο διαδίκτυο", "cs": "Žádné připojení k internetu",
    "hu": "Nincs internetkapcsolat", "ro": "Fără conexiune la internet",
    "uk": "Немає підключення до інтернету", "bg": "Няма интернет връзка",
    "hr": "Nema internetske veze", "sr": "Нема интернет везе",
    "sk": "Žiadne pripojenie k internetu", "ca": "Sense connexió a Internet",
    "tl": "Walang koneksyon sa Internet", "ms": "Tiada sambungan Internet",
    "fa": "اتصال اینترنت وجود ندارد", "sw": "Hakuna muunganisho wa mtandao",
    "ta": "இணைய இணைப்பு இல்லை", "te": "ఇంటర్నెట్ కనెక్షన్ లేదు",
    "ur": "انٹرنیٹ کنکشن نہیں ہے", "bn": "ইন্টারনেট সংযোগ নেই",
    "mr": "इंटरनेट कनेक्शन नाही", "gu": "ઇન્ટરનેટ કનેક્શન નથી",
    "pa": "ਇੰਟਰਨੈੱਟ ਕਨੈਕਸ਼ਨ ਨਹੀਂ ਹੈ",
    "kn": "ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕವಿಲ್ಲ", "ml": "ഇന്റർനെറ്റ് കണക്ഷൻ ഇല്ല",
    "am": "የበይነመረብ ግንኙነት የለም",
}

count = 0
for filename in os.listdir(LOCALES_DIR):
    if not filename.endswith('.json'):
        continue
    code = filename.replace('.json', '')
    filepath = os.path.join(LOCALES_DIR, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modified = False
    
    # Update dashboard.stats.eta to "Time Left"
    if 'dashboard' in data and 'stats' in data['dashboard']:
        new_val = TIME_LEFT_TRANSLATIONS.get(code, "Time Left")
        if data['dashboard']['stats'].get('eta') != new_val:
            data['dashboard']['stats']['eta'] = new_val
            modified = True
    
    # Add dashboard.no_internet
    if 'dashboard' in data:
        new_val = NO_INTERNET_TRANSLATIONS.get(code, "No Internet Connection")
        if data['dashboard'].get('no_internet') != new_val:
            data['dashboard']['no_internet'] = new_val
            modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        count += 1
        print(f"Updated: {filename}")

print(f"\nDone! Updated {count} locale files.")
