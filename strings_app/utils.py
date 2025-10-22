import hashlib
from collections import Counter

def analyze_string(value: str):
    cleaned = value.strip()
    length = len(cleaned)
    is_palindrome = cleaned.lower() == cleaned[::-1].lower()
    unique_chars = len(set(cleaned))
    word_count = len(cleaned.split())
    sha_hash = hashlib.sha256(cleaned.encode()).hexdigest()
    char_freq = dict(Counter(cleaned))

    return {
        "id": sha_hash,
        "value": cleaned,
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_chars,
        "word_count": word_count,
        "character_frequency_map": char_freq,
    }
