import os
import re

def validate_url(url):
    """
    Basic URL validation.
    """
    if not url:
        return False
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def is_pornhub(url):
    """
    Checks if the URL is from Pornhub.
    """
    if not url: return False
    return "pornhub.com" in url.lower()

def is_tiktok(url):
    """
    Checks if the URL is from TikTok.
    """
    if not url: return False
    return "tiktok.com" in url.lower()

def detect_site_info(url):
    """
    Returns a tuple (Site Name, Icon/Color Code, IsProtected).
    """
    if not url: 
        return None
    
    url_lower = url.lower()
    
    if "pornhub.com" in url_lower:
        return ("Pornhub", "🟧", True)
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return ("YouTube", "🟥", False) # Usually doesn't strictly require cookies for public vids
    elif "tiktok.com" in url_lower:
        return ("TikTok", "⚫", False)
    elif "facebook.com" in url_lower:
        return ("Facebook", "🔵", False)
    elif "instagram.com" in url_lower:
        return ("Instagram", "🟣", True) # Often needs login
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return ("Twitter/X", "🔷", False)
    elif "reddit.com" in url_lower:
        return ("Reddit", "🟠", False)
    elif "vimeo.com" in url_lower:
        return ("Vimeo", "🔵", False)
    elif "twitch.tv" in url_lower:
        return ("Twitch", "🟣", False)
    elif "dailymotion.com" in url_lower:
        return ("Dailymotion", "⬜", False)
    else:
        return ("General", "🌐", False)


def format_bytes(size):
    """
    Formats bytes into human readable string.
    """
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def format_seconds(seconds):
    """
    Formats seconds into MM:SS or HH:MM:SS.
    """
    if seconds is None:
        return "--:--"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    return f"{int(m):02d}:{int(s):02d}"
