def record_feedback(session_id: str, message: str, bot_reply: str, reward: float):
    with open('feedback.log', 'a', encoding='utf-8') as f:
        f.write(f"{session_id}\t{reward}\t{message}\t{bot_reply}\n")
    return True
