import math
import re
from datetime import datetime

def calculate_distance(lat1, lng1, lat2, lng2):
    if None in [lat1, lng1, lat2, lng2]:
        return float('inf')
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[\d\s\+\-\(\)]{10,15}$'
    return re.match(pattern, phone) is not None if phone else True

def format_datetime(dt):
    if isinstance(dt, str):
        return dt
    return dt.isoformat() if dt else None

def paginate(items, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end]

PROFANITY_WORDS = {'fuck':3, 'shit':2, 'damn':1, 'hell':1, 'bitch':3, 'asshole':3, 'ass':2}

def check_profanity(text):
    if not text:
        return {'score': 0, 'words': []}
    text_lower = text.lower()
    found = []
    score = 0
    for word, pts in PROFANITY_WORDS.items():
        if word in text_lower:
            found.append(word)
            score += pts
    return {'score': score, 'words': found, 'has_profanity': score > 0}