"""NLP utilities. Tries to use spaCy and HuggingFace transformers where available,
but falls back to rule-based implementations if not installed.
"""
from typing import Tuple, Dict
import os

# Rule-based fallback intent detection
INTENT_KEYWORDS = {
    'greeting': ['hello', 'hi', 'hey'],
    'bye': ['bye', 'goodbye', 'see you'],
    'help': ['help', 'support', 'assist'],
    'order_status': ['order', 'tracking', 'status', 'delivery'],
    'smalltalk': ['how are you', "what's up", 'how\'s it going']
}

def detect_intent_rule(text: str) -> str:
    t = text.lower()
    for intent, keys in INTENT_KEYWORDS.items():
        for k in keys:
            if k in t:
                return intent
    return 'unknown'

def extract_entities_rule(text: str) -> Dict[str,str]:
    ents = {}
    tokens = text.split()
    for tok in tokens:
        if tok.lower().startswith('#') or tok.lower().startswith('ord'):
            ents['order_id'] = tok.strip('.,')
        if '@' in tok and '.' in tok:
            ents['email'] = tok.strip('.,')
    return ents

def sentiment_rule(text: str) -> str:
    low = text.lower()
    if any(w in low for w in ['love', 'great', 'awesome', 'good', 'thanks']):
        return 'positive'
    if any(w in low for w in ['hate', 'bad', 'terrible', 'angry', 'frustrat']):
        return 'negative'
    return 'neutral'

# Try spaCy for NER and parsing
USE_SPACY = False
nlp_spacy = None
try:
    import spacy
    nlp_spacy = spacy.load('en_core_web_sm')
    USE_SPACY = True
except Exception as e:
    USE_SPACY = False

# Try HuggingFace sentiment pipeline
USE_HF_SENT = False
sentiment_pipe = None
try:
    from transformers import pipeline
    sentiment_pipe = pipeline('sentiment-analysis')
    USE_HF_SENT = True
except Exception:
    USE_HF_SENT = False

def detect_intent(text: str) -> str:
    return detect_intent_rule(text)

def extract_entities(text: str) -> Dict[str,str]:
    if USE_SPACY and nlp_spacy:
        doc = nlp_spacy(text)
        ents = {}
        for e in doc.ents:
            ents[e.label_.lower()] = e.text
        # keep simple 'order_id' and 'email' fallback as well
        ents.update(extract_entities_rule(text))
        return ents
    return extract_entities_rule(text)

def sentiment_analysis(text: str) -> str:
    if USE_HF_SENT and sentiment_pipe:
        try:
            r = sentiment_pipe(text[:512])[0]
            label = r.get('label','').lower()
            if 'pos' in label:
                return 'positive'
            if 'neg' in label:
                return 'negative'
            return 'neutral'
        except Exception:
            return sentiment_rule(text)
    return sentiment_rule(text)

def parse(text: str) -> Tuple[str, dict, str]:
    intent = detect_intent(text)
    entities = extract_entities(text)
    sentiment = sentiment_analysis(text)
    return intent, entities, sentiment
