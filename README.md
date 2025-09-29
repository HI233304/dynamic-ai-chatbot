 # Dynamic AI Chatbot — Enhanced (FastAPI)

Enhancements included:
- spaCy for NER and parsing (optional; falls back if not installed)
- HuggingFace Transformers sentiment pipeline (optional; falls back)
- Offline local response generator (simple Markov-chain based) when OpenAI not available
- UI enhancements: timestamps, typing indicator, download chat history

Quickstart:
1. Create venv and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm  # optional but recommended
```

2. Set `OPENAI_API_KEY` to enable real GPT fallback (optional).
3. Run: `uvicorn app:app --reload --port 8000`
