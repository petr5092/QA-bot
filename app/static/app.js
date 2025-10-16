const form = document.getElementById('chat-form');
const input = document.getElementById('question');
const log = document.getElementById('chat-log');
const modelContent = document.getElementById('model-content');

function appendMessage(who, text) {
  const el = document.createElement('div');
  el.className = 'message ' + (who === 'user' ? 'user' : 'bot');
  el.innerText = (who === 'user' ? 'Вы: ' : 'Капелька: ') + text;
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
    const messageEl = appendMessage('bot', text);

    const intentVideoMap = {
    };
    const videoUrl = data.video || (data.intent ? intentVideoMap[data.intent] : null);
    if (videoUrl) {
      renderModelVideo(videoUrl);
    }
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
appendMessage('bot', 'Привет! Я Капелька. Спросите меня что-нибудь.');

function renderModelVideo(url, options = {}) {
  modelContent.innerHTML = '';
  const wrap = document.createElement('div');
  wrap.className = 'model-video';
  if (options.type === 'iframe') {
    const iframe = document.createElement('iframe');
    iframe.src = url;
    iframe.width = '100%';
    iframe.height = '240';
    iframe.frameBorder = '0';
    wrap.appendChild(iframe);
  } else if (options.type === 'image') {
    const img = document.createElement('img');
    img.src = url;
    img.style.width = '100%';
    img.style.borderRadius = '6px';
    wrap.appendChild(img);
  } else {
    const v = document.createElement('video');
    v.controls = true;
    v.src = url;
    wrap.appendChild(v);
  }
  modelContent.appendChild(wrap);
}


document.addEventListener('DOMContentLoaded', () => {

renderModelVideo('/files/Hi.gif', { type: 'image' });
  setTimeout(() => {
    renderModelVideo('/files/Eat.gif', { type: 'image' });
  }, 2012);
});
