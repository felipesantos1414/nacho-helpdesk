// ── Nacho HelpDesk Chat JS ───────────────────────────────

const messagesEl = document.getElementById('messages');
const inputEl    = document.getElementById('userInput');
const sendBtn    = document.getElementById('sendBtn');
const inputWrap  = document.getElementById('inputWrap');

let sessionClosed = false;
let currentLang   = localStorage.getItem('nacho-lang') || 'pt';

// ── Language System ───────────────────────────────────────
function t(key) {
  return TRANSLATIONS[currentLang][key] || TRANSLATIONS['pt'][key] || key;
}

function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem('nacho-lang', lang);

  // Flag button active states
  document.getElementById('flagPT').classList.toggle('flag-active', lang === 'pt');
  document.getElementById('flagEN').classList.toggle('flag-active', lang === 'en');

  // All data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (TRANSLATIONS[lang][key] !== undefined) {
      el.textContent = TRANSLATIONS[lang][key];
    }
  });

  // Input placeholder
  inputEl.placeholder = t('placeholder');

  // Welcome message (only update if it still exists unmodified)
  const w1 = document.getElementById('welcomeText1');
  const w2 = document.getElementById('welcomeText2');
  if (w1) w1.innerHTML = t('welcomeText1');
  if (w2) w2.innerHTML = t('welcomeText2');

  // Welcome category tags
  const catsEl = document.getElementById('welcomeCats');
  if (catsEl) {
    catsEl.innerHTML = t('welcomeCats').map(c =>
      `<span class="cat-tag">${c}</span>`
    ).join('');
  }

  // Rebuild chips with translated messages
  const chips = document.getElementById('chipsContainer');
  if (chips) {
    chips.innerHTML = t('chips').map(c =>
      `<button class="chip" onclick="quickSend('${c.msg}')">${c.label}</button>`
    ).join('');
  }
}

// ── Send Message ──────────────────────────────────────────
async function sendMessage() {
  if (sessionClosed) return;
  const text = inputEl.value.trim();
  if (!text) return;

  appendUserMsg(text);
  inputEl.value = '';
  setLoading(true);

  try {
    const res  = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, lang: currentLang })
    });
    const data = await res.json();

    removeTyping();
    appendBotMsg(data.response, data.problem_id, data.show_feedback);

    if (data.closed) {
      sessionClosed = true;
      lockInput();
    }
  } catch (err) {
    removeTyping();
    const errMsg = currentLang === 'en'
      ? 'Woof! 🐾 A connection error occurred. Please try again.'
      : 'Au! 🐾 Ocorreu um erro de conexão. Por favor, tente novamente.';
    appendBotMsg(errMsg, null, false);
  }

  setLoading(false);
}

// ── Quick Send from sidebar chips ────────────────────────
function quickSend(text) {
  if (sessionClosed) return;
  inputEl.value = text;
  sendMessage();
}

// ── Render user message ───────────────────────────────────
function appendUserMsg(text) {
  const row = document.createElement('div');
  row.className = 'msg-row user';
  row.innerHTML = `<div class="msg-bubble user">${escapeHtml(text)}</div>`;
  messagesEl.appendChild(row);
  showTyping();
  scrollToBottom();
}

// ── Render bot message ────────────────────────────────────
function appendBotMsg(text, problemId, showFeedback) {
  const row = document.createElement('div');
  row.className = 'msg-row bot';

  const formatted = formatBotText(text);
  let feedbackHtml = '';
  if (showFeedback && problemId) {
    feedbackHtml = `
      <div class="feedback-wrap" id="fb-${problemId}">
        <span>${t('didItHelp')}</span>
        <button class="fb-btn yes" onclick="sendFeedback(${problemId}, true, this)">${t('yes')}</button>
        <button class="fb-btn no"  onclick="sendFeedback(${problemId}, false, this)">${t('no')}</button>
      </div>`;
  }

  row.innerHTML = `
    <div class="msg-avatar-photo"><img src="/static/images/nacho-photo.png" alt="Nacho"></div>
    <div class="msg-bubble bot">${formatted}${feedbackHtml}</div>`;

  messagesEl.appendChild(row);
  scrollToBottom();
}

// ── Feedback ──────────────────────────────────────────────
async function sendFeedback(problemId, helpful, btn) {
  const wrap = btn.closest('.feedback-wrap');
  if (!wrap) return;
  wrap.querySelectorAll('.fb-btn').forEach(b => b.disabled = true);

  await fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ problem_id: problemId, helpful })
  });

  wrap.innerHTML = helpful
    ? `<span style="color:var(--green-ok);font-weight:600">${t('thankYes')}</span>`
    : `<span style="color:var(--brown-warm);font-weight:600">${t('thankNo')}</span>`;
}

// ── New Session ───────────────────────────────────────────
async function newSession() {
  await fetch('/api/new-session', { method: 'POST' });
  location.reload();
}

// ── Typing indicator ──────────────────────────────────────
function showTyping() {
  const row = document.createElement('div');
  row.className = 'msg-row bot';
  row.id = 'typing-indicator';
  row.innerHTML = `
    <div class="msg-avatar-photo"><img src="/static/images/nacho-photo.png" alt="Nacho"></div>
    <div class="msg-bubble bot">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;
  messagesEl.appendChild(row);
  scrollToBottom();
}

function removeTyping() {
  const t = document.getElementById('typing-indicator');
  if (t) t.remove();
}

// ── Helpers ───────────────────────────────────────────────
function setLoading(state) {
  sendBtn.disabled = state;
  inputEl.disabled = state;
}

function lockInput() {
  inputWrap.classList.add('disabled');
  inputEl.disabled = true;
  sendBtn.disabled = true;
  const hint = document.querySelector('.input-hint');
  if (hint) {
    hint.innerHTML = `🔒 ${currentLang === 'en' ? 'Session ended —' : 'Sessão encerrada —'} <a href="/" onclick="newSession();return false;" style="color:var(--brown-warm)">${t('sessionClosedLink')}</a>`;
  }
  const banner = document.createElement('div');
  banner.className = 'session-closed';
  banner.textContent = t('sessionClosed');
  document.querySelector('.chat-input-area').prepend(banner);
}

function scrollToBottom() {
  requestAnimationFrame(() => { messagesEl.scrollTop = messagesEl.scrollHeight; });
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatBotText(text) {
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  const lines = html.split('\n');
  const out = [];
  let inList = false;
  for (const line of lines) {
    const numbered = line.match(/^(\d+)\.\s+(.+)/);
    if (numbered) {
      if (!inList) { out.push('<ol>'); inList = true; }
      out.push(`<li>${numbered[2]}</li>`);
    } else {
      if (inList) { out.push('</ol>'); inList = false; }
      if (line.trim()) out.push(`<p>${line}</p>`);
    }
  }
  if (inList) out.push('</ol>');
  return out.join('');
}

// ── Init ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  applyLang(currentLang);
  inputEl.focus();
});
