(function(){
  const API_URL = window.location.origin;
  const STORAGE_KEY = 'chat_session_id';
  const TOKEN_KEY = 'user_token';

  function getSessionId(){
    let id = localStorage.getItem(STORAGE_KEY);
    if(!id){ id = 'sess_' + Math.random().toString(36).slice(2) + Date.now(); localStorage.setItem(STORAGE_KEY, id); }
    return id;
  }

  function getToken(){ return localStorage.getItem(TOKEN_KEY) || null; }

  const styles = `
  .crw-chat-toggle{position:fixed;right:20px;bottom:20px;width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;box-shadow:0 8px 20px rgba(0,0,0,.2);cursor:pointer;z-index:9999;font-size:24px;display:flex;align-items:center;justify-content:center}
  .crw-chat-panel{position:fixed;right:20px;bottom:90px;width:320px;max-height:70vh;background:#fff;border-radius:12px;box-shadow:0 12px 30px rgba(0,0,0,.2);display:none;flex-direction:column;overflow:hidden;z-index:9999}
  .crw-chat-header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:12px 14px;display:flex;align-items:center;justify-content:space-between}
  .crw-chat-title{font-weight:600}
  .crw-chat-body{padding:10px;background:#f7f7fb;overflow:auto;height:360px}
  .crw-msg{display:flex;margin:8px 0}
  .crw-msg-user{justify-content:flex-end}
  .crw-bubble{max-width:80%;padding:10px 12px;border-radius:12px;font-size:14px;line-height:1.3;box-shadow:0 2px 8px rgba(0,0,0,.05)}
  .crw-bubble-user{background:#667eea;color:#fff;border-bottom-right-radius:4px}
  .crw-bubble-bot{background:#fff;color:#333;border-bottom-left-radius:4px}
  .crw-chat-input{display:flex;padding:8px;border-top:1px solid #eee;background:#fff}
  .crw-chat-input input{flex:1;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px}
  .crw-chat-input button{margin-left:8px;padding:10px 12px;border:none;border-radius:8px;background:#667eea;color:#fff;cursor:pointer}
  .crw-tools{padding:8px;background:#fff;border-top:1px solid #eee;display:flex;gap:8px}
  .crw-tool{flex:1;padding:8px;border-radius:8px;background:#eef2ff;color:#3949ab;border:1px solid #c7d2fe;cursor:pointer;font-size:12px}
  @media(max-width:480px){.crw-chat-panel{right:10px;left:10px;width:auto;}}
  `;
  const styleEl = document.createElement('style');
  styleEl.innerText = styles;
  document.head.appendChild(styleEl);

  const toggle = document.createElement('button');
  toggle.className = 'crw-chat-toggle';
  toggle.title = 'Chat with us';
  toggle.innerHTML = '💬';

  const panel = document.createElement('div');
  panel.className = 'crw-chat-panel';
  panel.innerHTML = `
    <div class="crw-chat-header">
      <div class="crw-chat-title">Assistant</div>
      <button id="crwClose" style="background:transparent;border:none;color:#fff;font-size:18px;cursor:pointer">✕</button>
    </div>
    <div id="crwBody" class="crw-chat-body"></div>
    <div class="crw-tools">
      <button id="crwStartPlan" class="crw-tool">Start Trip Planner</button>
      <button id="crwHistory" class="crw-tool">History</button>
    </div>
    <div class="crw-chat-input">
      <input id="crwInput" placeholder="Type a message..." />
      <button id="crwSend">Send</button>
    </div>
  `;

  document.body.appendChild(toggle);
  document.body.appendChild(panel);

  const bodyEl = panel.querySelector('#crwBody');
  const inputEl = panel.querySelector('#crwInput');
  const sendBtn = panel.querySelector('#crwSend');
  const startPlanBtn = panel.querySelector('#crwStartPlan');
  const historyBtn = panel.querySelector('#crwHistory');

  function appendMsg(text, role){
    const wrap = document.createElement('div');
    wrap.className = 'crw-msg ' + (role==='user'?'crw-msg-user':'');
    const bub = document.createElement('div');
    bub.className = 'crw-bubble ' + (role==='user'?'crw-bubble-user':'crw-bubble-bot');
    bub.innerText = text;
    wrap.appendChild(bub);
    bodyEl.appendChild(wrap);
    bodyEl.scrollTop = bodyEl.scrollHeight;
  }

  // Planner workflow
  const planQuestions = [
    { key: 'name', label: 'Your full name' },
    { key: 'address', label: 'Your address' },
    { key: 'city', label: 'Your city' },
    { key: 'phone', label: 'Your phone number' },
    { key: 'destination', label: 'Where do you want to visit?' },
    { key: 'query', label: 'Any specific query or preference?' },
    { key: 'budget', label: 'Your budget (₹)' },
    { key: 'days', label: 'Number of days for the trip' }
  ];
  let inPlanner = false;
  let plannerStep = 0;
  let answers = {};

  function startPlanner(){
    inPlanner = true; plannerStep = 0; answers = {};
    appendMsg('Great! I will ask you a few questions to plan your trip. You can type "cancel" anytime to stop.', 'assistant');
    askNext();
  }
  function askNext(){
    if(plannerStep < planQuestions.length){
      appendMsg(planQuestions[plannerStep].label + ':', 'assistant');
    } else {
      inPlanner = false;
      const summary =
        `Here is what I gathered:\n`+
        `• Name: ${answers.name || ''}\n`+
        `• Address: ${answers.address || ''}\n`+
        `• City: ${answers.city || ''}\n`+
        `• Phone: ${answers.phone || ''}\n`+
        `• Destination: ${answers.destination || ''}\n`+
        `• Query: ${answers.query || ''}\n`+
        `• Budget: ${answers.budget || ''}\n`+
        `• Days: ${answers.days || ''}`;
      appendMsg(summary, 'assistant');
    }
  }

  function handlePlannerInput(text){
    if(text.toLowerCase() === 'cancel'){
      inPlanner = false; appendMsg('Trip planner cancelled. You can start again anytime.', 'assistant'); return;
    }
    const q = planQuestions[plannerStep];
    // Basic validations
    if(q.key === 'phone' && !/^[0-9 +\-]{6,15}$/.test(text)){ appendMsg('Please enter a valid phone number.', 'assistant'); return; }
    if(q.key === 'budget' && isNaN(Number(text))){ appendMsg('Please enter a numeric budget (₹).', 'assistant'); return; }
    if(q.key === 'days' && (isNaN(Number(text)) || Number(text) <= 0)){ appendMsg('Please enter a valid number of days.', 'assistant'); return; }
    answers[q.key] = text;
    plannerStep += 1;
    askNext();
  }

  async function loadHistory(){
    try{
      const session_id = getSessionId();
      const res = await fetch(`${API_URL}/api/chat/history?session_id=${encodeURIComponent(session_id)}&limit=50`);
      const data = await res.json();
      bodyEl.innerHTML = '';
      (data.messages||[]).forEach(m => appendMsg(m.message, m.role));
    }catch(e){ /* ignore */ }
  }

  async function sendMessage(){
    const text = inputEl.value.trim();
    if(!text) return;
    inputEl.value = '';
    appendMsg(text, 'user');

    if(inPlanner){
      handlePlannerInput(text);
      return;
    }

    try{
      const payload = { session_id: getSessionId(), message: text };
      const t = getToken(); if(t) payload.token = t;
      const res = await fetch(`${API_URL}/api/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      appendMsg(data.reply || 'Thanks! We will get back to you.', 'assistant');
    }catch(e){ appendMsg('Network error. Please try again.', 'assistant'); }
  }

  toggle.addEventListener('click', ()=>{
    const visible = panel.style.display === 'flex';
    panel.style.display = visible ? 'none' : 'flex';
    if(!visible){ loadHistory(); }
  });
  panel.querySelector('#crwClose').addEventListener('click', ()=> panel.style.display = 'none');
  sendBtn.addEventListener('click', sendMessage);
  inputEl.addEventListener('keydown', (e)=>{ if(e.key === 'Enter'){ e.preventDefault(); sendMessage(); }});
  startPlanBtn.addEventListener('click', startPlanner);
  historyBtn.addEventListener('click', loadHistory);
})();
