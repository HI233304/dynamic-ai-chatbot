"""Response generation with offline local generator fallback (simple Markov chain).
"""
import os, random, time, asyncio
from typing import Dict, Any
from .nlp import detect_intent

try:
    import openai
except Exception:
    openai = None

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

RULES = {
    'greeting': ['Hello! How can I help you today?', 'Hi there — what can I do for you?'],
    'bye': ['Goodbye — have a great day!', 'See you later!'],
    'help': ['I can help with orders, account questions, or general info. What do you need?'],
    'unknown': ["I'm not sure I understand. Can you rephrase?", "I don't have an answer for that yet — want me to try searching?"]
}

# Simple Markov chain generator built from recent conversation
class SimpleMarkov:
    def __init__(self):
        self.chain = {}

    def feed(self, text: str):
        # tokenize on spaces
        tokens = text.split()
        if not tokens: return
        for i in range(len(tokens)-1):
            k = tokens[i].lower()
            nxt = tokens[i+1]
            self.chain.setdefault(k, []).append(nxt)

    def generate(self, seed=None, max_words=30):
        if not self.chain:
            return ''
        if seed and seed.lower() in self.chain:
            cur = seed.lower()
        else:
            cur = random.choice(list(self.chain.keys()))
        words = [cur]
        for _ in range(max_words-1):
            nxts = self.chain.get(cur)
            if not nxts:
                break
            nxt = random.choice(nxts)
            words.append(nxt)
            cur = nxt.lower()
        return ' '.join(words).capitalize() + '.'

# instantiate a singleton simple generator
_local_gen = SimpleMarkov()

async def generate_reply(message: str, intent: str=None, entities: Dict=None, sentiment: str=None, session_id: str=None, memory=None) -> str:
    intent = intent or detect_intent(message)
    # 1) Rule-based immediate responses
    if intent in RULES:
        # simulate typing latency
        await asyncio.sleep(0.4)
        return random.choice(RULES[intent])
    # 2) Entities handling
    if entities and 'order_id' in entities:
        await asyncio.sleep(0.4)
        return f'I found order `{entities["order_id"]}`. Would you like an update?'
    # 3) Sentiment-based response
    if sentiment == 'negative':
        await asyncio.sleep(0.4)
        return 'I'"m sorry you had a bad experience. Tell me more and I will assist."
    # 4) Try OpenAI if configured
    if openai is not None and OPENAI_API_KEY:
        try:
            openai.api_key = OPENAI_API_KEY
            prompt = build_prompt(message, session_id, memory)
            resp = openai.ChatCompletion.create(model='gpt-4o-mini', messages=prompt, max_tokens=200)
            text = resp['choices'][0]['message']['content'].strip()
            return text
        except Exception:
            pass
    # 5) Build local generator from context and generate
    if memory:
        ctx = memory.get_context(session_id, limit=20)
        for m in ctx:
            _local_gen.feed(m.get('text',''))
    # ensure current message feeds generator too
    _local_gen.feed(message)
    # tiny delay to simulate thinking/typing
    await asyncio.sleep(min(1.0, 0.2 + len(message)/100.0))
    out = _local_gen.generate(seed=message.split()[0] if message.split() else None)
    if not out:
        return random.choice(RULES['unknown'])
    return out
