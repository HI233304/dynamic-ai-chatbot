import sqlite3, os, time, json
DB = os.path.join(os.getcwd(), 'chat_analytics.db')

def _conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        user_message TEXT,
        bot_reply TEXT,
        intent TEXT,
        sentiment TEXT,
        ts INTEGER
    )''')
    conn.commit()
    conn.close()

def log_interaction(session_id, user_message, bot_reply, intent, sentiment):
    init_db()
    conn = _conn()
    c = conn.cursor()
    c.execute('INSERT INTO interactions (session_id,user_message,bot_reply,intent,sentiment,ts) VALUES (?,?,?,?,?,?)',
              (session_id, user_message, bot_reply, intent, sentiment, int(time.time())))
    conn.commit()
    conn.close()

def get_stats():
    init_db()
    conn = _conn()
    c = conn.cursor()
    total = c.execute('SELECT COUNT(*) as c FROM interactions').fetchone()['c']
    by_intent = dict((row['intent'], row['c']) for row in c.execute('SELECT intent, COUNT(*) as c FROM interactions GROUP BY intent'))
    recent = [dict(r) for r in c.execute('SELECT session_id,user_message,bot_reply,ts FROM interactions ORDER BY ts DESC LIMIT 20')]
    conn.close()
    return {'total': total, 'by_intent': by_intent, 'recent': recent}
