import re
from typing import Dict, Any

class NLParseError(Exception):
    pass

def parse_natural_language_query(text: str) -> Dict[str, Any]:
    """
    Very small heuristic NLP parser that returns a dict of filters.
    Supported translations:
      - "single word" -> word_count = 1
      - "palindromic" or "palindrome" -> is_palindrome = True
      - "strings longer than X characters" -> min_length = X+1
      - "strings shorter than X characters" -> max_length = X-1
      - "containing the letter X" / "containing X" -> contains_character = x
      - "strings containing the letter z" -> contains_character=z
      - "strings containing the letter 'a' and palindromic" (will parse both heuristics)
    """
    original = text
    t = text.lower().strip()
    filters = {}

    # single word
    if re.search(r'\bsingle[- ]word\b', t):
        filters["word_count"] = 1

    # palindromic
    if re.search(r'\bpalindrom(e|ic|al)\b', t):
        filters["is_palindrome"] = True

    # longer than X characters or longer than X
    m = re.search(r'longer than (\d+)', t)
    if m:
        n = int(m.group(1))
        filters["min_length"] = n + 1  # "longer than 10" => min_length 11

    # strings longer than or equal to X (rare phrase)
    m = re.search(r'longer than or equal to (\d+)', t)
    if m:
        filters["min_length"] = int(m.group(1))

    # shorter than X
    m = re.search(r'shorter than (\d+)', t)
    if m:
        filters["max_length"] = int(m.group(1)) - 1

    # exact "length" e.g. "length of 5"
    m = re.search(r'length (?:of )?(\d+)', t)
    if m:
        filters["min_length"] = int(m.group(1))
        filters["max_length"] = int(m.group(1))

    # contains character
    m = re.search(r'contain(?:ing|s)?(?: the )?letter[s]? ?(?:\'|"|)?([a-z0-9])(?:\'|"|)?', t)
    if not m:
        m = re.search(r'contain(?:ing|s)? ?([a-z0-9])\b', t)
    if m:
        filters["contains_character"] = m.group(1)

    if not filters:
        raise NLParseError("Unable to parse natural language query into filters")

    return {
        "original": original,
        "parsed_filters": filters
    }
