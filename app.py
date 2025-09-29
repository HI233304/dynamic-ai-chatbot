from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio, json

from chatbot import nlp, memory, response, analytics

app = FastAPI(title='Dynamic AI Chatbot - Enhanced')
templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')

conv_store = memory.ConversationMemory()

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/api/chat')
async def chat_api(message: str = Form(...), session_id: str = Form(None)):
    session_id = session_id or 'default'
    conv_store.add_user_message(session_id, message)
    intent, entities, sentiment = nlp.parse(message)
    # Indicate typing by returning a 'typing' event to frontend before generating (frontend shows indicator)
    reply = await response.generate_reply(message, intent=intent, entities=entities, sentiment=sentiment, session_id=session_id, memory=conv_store)
    conv_store.add_bot_message(session_id, reply)
    analytics.log_interaction(session_id, message, reply, intent, sentiment)
    return JSONResponse({'reply': reply, 'intent': intent, 'entities': entities, 'sentiment': sentiment})

@app.get('/api/export/{session_id}')
async def export_session(session_id: str):
    data = conv_store.get_history(session_id)
    path = f'/tmp/chat_history_{session_id}.json'
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return FileResponse(path, media_type='application/json', filename=f'chat_history_{session_id}.json')

@app.get('/dashboard', response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = analytics.get_stats()
    return templates.TemplateResponse('dashboard.html', {'request': request, 'stats': stats})

@app.get('/health')
async def health():
    return {'status': 'ok'}
