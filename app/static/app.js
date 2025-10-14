const form = document.getElementById('chat-form');
const input = document.getElementById('question');
const log = document.getElementById('chat-log');

function appendMessage(who, text) {
  const el = document.createElement('div');
  el.className = 'message ' + (who === 'user' ? 'user' : 'bot');
  el.innerText = (who === 'user' ? 'Вы: ' : 'Бот: ') + text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

async function sendQuestion(q) {
  appendMessage('user', q);
  try {
    const res = await fetch('/chat/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });
    if (!res.ok) {
      const txt = await res.text();
      appendMessage('bot', 'Ошибка сервера: ' + txt);
      return;
    }
    const data = await res.json();
    let text = data.answer;
    appendMessage('bot', text);
  } catch (err) {
    appendMessage('bot', 'Сетевая ошибка: ' + err.message);
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  input.value = '';
  sendQuestion(q);
});

// Initial message
appendMessage('bot', 'Привет! Я QA-бот. Спросите меня что-нибудь.');
