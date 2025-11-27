(function() {
  const stateKey = 'ver-chatbot-state';
  const elements = {};

  function saveState(state) {
    localStorage.setItem(stateKey, JSON.stringify(state));
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(stateKey);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function createMessage(text, sender = 'bot') {
    const bubble = document.createElement('div');
    bubble.className = `chatbot-message ${sender}`;
    bubble.textContent = text;
    return bubble;
  }

  function renderTyping() {
    const wrap = document.createElement('div');
    wrap.className = 'chatbot-message bot';
    wrap.innerHTML = '<div class="chatbot-typing"><span></span><span></span><span></span></div>';
    return wrap;
  }

  function scrollToBottom() {
    elements.body.scrollTop = elements.body.scrollHeight;
  }

  function appendBotMessage(text, delay = 400) {
    const typing = renderTyping();
    elements.body.appendChild(typing);
    scrollToBottom();

    setTimeout(() => {
      elements.body.removeChild(typing);
      elements.body.appendChild(createMessage(text, 'bot'));
      scrollToBottom();
    }, delay);
  }

  function appendUserMessage(text) {
    elements.body.appendChild(createMessage(text, 'user'));
    scrollToBottom();
  }

  async function sendToTelegram(formData) {
    const token = 'YOUR_BOT_TOKEN';
    const chatId = 'YOUR_CHAT_ID';
    const text = `
🚀 Нова заявка (Ads):
👤 Ім'я: ${formData.get('name')}
📧 Email: ${formData.get('email')}
✈️ Telegram: ${formData.get('telegram') || 'Не вказано'}
📝 Повідомлення: ${formData.get('message')}
    `;

    try {
      await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId, text })
      });
      return true;
    } catch (e) {
      console.error(e);
      return false;
    }
  }

  function persistHistory(history, step, answers) {
    saveState({ history: history.map(h => ({ sender: h.sender, text: h.text })), step, answers });
  }

  function restoreHistory(state) {
    if (!state?.history?.length) return { history: [], step: 'welcome', answers: {} };
    state.history.forEach(item => {
      elements.body.appendChild(createMessage(item.text, item.sender));
    });
    return { history: state.history, step: state.step || 'welcome', answers: state.answers || {} };
  }

  function setActions(actions = []) {
    elements.actions.innerHTML = '';
    actions.forEach(action => {
      const btn = document.createElement('button');
      btn.className = 'chatbot-chip';
      btn.textContent = action.label;
      btn.addEventListener('click', () => action.onClick(action.label));
      elements.actions.appendChild(btn);
    });
  }

  function showInput(placeholder, onSubmit) {
    elements.actions.innerHTML = '';
    const row = document.createElement('div');
    row.className = 'chatbot-input-row';
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = placeholder;
    const submit = document.createElement('button');
    submit.className = 'chatbot-submit';
    submit.textContent = 'Надіслати';

    submit.addEventListener('click', () => {
      const value = input.value.trim();
      if (!value) return;
      onSubmit(value);
    });

    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        submit.click();
      }
    });

    row.append(input, submit);
    elements.actions.appendChild(row);
    input.focus();
  }

  function runFlow() {
    const stored = restoreHistory(loadState());
    let { step, answers, history } = stored;

    function goTo(nextStep) {
      step = nextStep;
      persistHistory(history, step, answers);
      handleStep();
    }

    function handleStep() {
      switch (step) {
        case 'welcome':
          setActions([
            { label: '🚀 Почати', onClick: () => { appendUserMessage('Почати'); history.push({ sender: 'user', text: 'Почати' }); goTo('niche'); } },
            { label: 'Ні, дякую', onClick: () => { appendUserMessage('Ні, дякую'); history.push({ sender: 'user', text: 'Ні, дякую' }); appendBotMessage('Якщо передумаєте — я завжди тут.'); persistHistory(history, step, answers); } }
          ]);
          if (!history.length) {
            appendBotMessage("Вітаю! Я AI-помічник Vermarkter. Давайте підберемо стратегію для вашого бізнесу в ЄС. Це займе 30 секунд.");
          }
          break;
        case 'niche':
          appendBotMessage('Яка у вас сфера діяльності?');
          setActions([
            { label: 'E-commerce', onClick: (label) => { answers.niche = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('geo'); } },
            { label: 'Послуги', onClick: (label) => { answers.niche = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('geo'); } },
            { label: 'B2B/Виробництво', onClick: (label) => { answers.niche = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('geo'); } },
            { label: 'Інфобизнес', onClick: (label) => { answers.niche = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('geo'); } }
          ]);
          break;
        case 'geo':
          appendBotMessage('Де плануєте продавати?');
          setActions([
            { label: 'Німеччина 🇩🇪', onClick: (label) => { answers.geo = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('site'); } },
            { label: 'Польща 🇵🇱', onClick: (label) => { answers.geo = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('site'); } },
            { label: 'Вся Європа 🇪🇺', onClick: (label) => { answers.geo = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('site'); } },
            { label: 'Інше', onClick: (label) => { answers.geo = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('site'); } }
          ]);
          break;
        case 'site':
          appendBotMessage('Чи є у вас готовий сайт?');
          setActions([
            { label: 'Так', onClick: (label) => { answers.site = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('lead'); } },
            { label: 'Потрібен аудит', onClick: (label) => { answers.site = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('lead'); } },
            { label: 'Треба створити', onClick: (label) => { answers.site = label; appendUserMessage(label); history.push({ sender: 'user', text: label }); goTo('lead'); } }
          ]);
          break;
        case 'lead':
          appendBotMessage('Я підготував чек-лист запуску. Куди надіслати?');
          showInput('Email або Telegram', (value) => {
            answers.contact = value;
            appendUserMessage(value);
            history.push({ sender: 'user', text: value });
            goTo('final');
          });
          break;
        case 'final':
          appendBotMessage('Записую. Відправляю чек-лист і стратегію.');
          setActions([]);
          const payload = new FormData();
          payload.set('name', answers.niche || 'Клієнт');
          payload.set('email', answers.contact || 'Не вказано');
          payload.set('telegram', answers.contact || '');
          payload.set('message', `Ніша: ${answers.niche || '-'}, Гео: ${answers.geo || '-'}, Сайт: ${answers.site || '-'}`);
          sendToTelegram(payload).then(() => {
            appendBotMessage('Готово! Ми напишемо вам протягом 10 хвилин.');
          });
          persistHistory(history, step, answers);
          break;
        default:
          goTo('welcome');
      }
    }

    handleStep();
  }

  function init() {
    elements.shell = document.querySelector('.chatbot-shell');
    elements.window = document.getElementById('chatbot-window');
    elements.body = document.getElementById('chatbot-body');
    elements.actions = document.getElementById('chatbot-actions');
    elements.toggle = document.getElementById('chatbot-toggle');
    elements.close = document.getElementById('chatbot-close');

    if (!elements.shell || !elements.window || !elements.body || !elements.actions || !elements.toggle || !elements.close) return;

    elements.toggle.addEventListener('click', () => {
      elements.window.classList.toggle('open');
      document.body.style.overflow = elements.window.classList.contains('open') ? 'hidden' : '';
    });

    elements.close.addEventListener('click', () => {
      elements.window.classList.remove('open');
      document.body.style.overflow = '';
    });

    window.openChatbot = () => {
      elements.window.classList.add('open');
      document.body.style.overflow = 'hidden';
      elements.toggle.focus();
    };

    runFlow();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
