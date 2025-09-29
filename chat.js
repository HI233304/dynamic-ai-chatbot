const form = document.getElementById('chat-form');
const messages = document.getElementById('messages');
const typing = document.getElementById('typing');
const downloadBtn = document.getElementById('download');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const msgInput = document.getElementById('message');
  const sessionId = document.getElementById('session_id').value || 'default';
  const text = msgInput.value.trim();
  if (!text) return;
  appendMsg('user', text);
  msgInput.value = '';
  // show typing indicator
  typing.style.display = 'block';
  const data = new FormData();
  data.append('message', text);
  data.append('session_id', sessionId);
  try{
    const res = await fetch('/api/chat', { method: 'POST', body: data });
    const json = await res.json();
    // hide typing
    typing.style.display = 'none';
    appendMsg('bot', json.reply);
  }catch(err){
    typing.style.display = 'none';
    appendMsg('bot', 'Error: could not reach server.');
  }
});

downloadBtn.addEventListener('click', async () => {
  const sessionId = document.getElementById('session_id').value || 'default';
  const url = `/api/export/${sessionId}`;
  const res = await fetch(url);
  if (res.ok){
    const blob = await res.blob();
    const urlBlob = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = urlBlob;
    a.download = `chat_history_${sessionId}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } else {
    alert('Could not export chat history.');
  }
});

function appendMsg(who, txt){
  const div = document.createElement('div');
  div.className = 'message ' + (who === 'user' ? 'user' : 'bot');
  const now = new Date();
  const ts = now.toLocaleString();
  div.innerHTML = '<div>' + (who === 'user' ? 'You: ' : 'Bot: ') + escapeHtml(txt) + '</div>' +
                  '<div class="timestamp">' + ts + '</div>';
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(unsafe) {
    return unsafe.replace(/[&<"'>]/g, function(m) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'})[m]; });
}
