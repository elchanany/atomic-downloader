# Localization Dictionary
# This file contains all the text strings used in the application.

STRINGS = {
    "he": {
        "app_title": "🚀 ATOMIC DOWNLOADER // IL",
        "header_title": "ATOMIC",
        "header_subtitle": "מערכת הורדות מתקדמת",
        "url_placeholder": "הדבק קישור כאן... (YouTube, TikTok, Pornhub)",
        "paste_btn": "הדבק 📋",
        "download_btn": "הפעל מנועים והורד 🚀",
        "downloading_btn": "מבצע הורדה...",
        "status_ready": "המערכת מוכנה לפקודה.",
        "status_initializing": "מנתח נתונים...",
        "status_downloading": "בתהליך הורדה... {percent}%",
        "status_complete": "✅ המשימה הושלמה בהצלחה!",
        "status_error": "❌ שגיאה קריטית",
        "settings_save_path": "תיקיית יעד",
        "settings_browse": "שנה...",
        "settings_cookies": "קוקיז (לאתרים מוגנים):",
        "login_btn": "🔓 בצע פריצת אבטחה (התחברות)",
        "login_btn_loading": "פותח מסוף התחברות...",
        "login_instructions": "⚠️ המערכת זיהתה אתר מוגן! נדרשת גישה.",
        "log_expand_btn": "בחון לוגים טכניים 💻",
        "log_collapse_btn": "סגור מסוף לוגים ✖️",
        "site_detected": "זיהוי יעד: {site}",
        "unknown_site": "יעד כללי",
        "stats_speed": "מהירות רשת",
        "stats_eta": "זמן משוער",
        "stats_size": "נפח קובץ",
        "error_no_url": "⚠️ נדרש קישור תקין לביצוע הפעולה!",
        "login_success_title": "גישה אושרה",
        "login_success_msg": "ההתחברות הצליחה! מפתחות הגישה נשמרו.",
        "login_fail_title": "גישה נדחתה",
        "login_fail_msg": "לא הצלחנו לשמור את הקוקיז. נסה שוב.",
    }
}

CURRENT_LANG = "he"

def get_str(key, **kwargs):
    lang_dict = STRINGS.get(CURRENT_LANG, STRINGS["he"])
    text = lang_dict.get(key, f"MISSING: {key}")
    try:
        return text.format(**kwargs)
    except:
        return text
