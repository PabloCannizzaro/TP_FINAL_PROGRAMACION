// Improved SPA logic: rendering, drag/drop, a11y, loading/error handling.
const api = {
  async post(url, body) {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {})
    });
    if (!r.ok) throw new Error((await r.text()) || `HTTP ${r.status}`);
    return r.json();
  },
  async get(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error((await r.text()) || `HTTP ${r.status}`);
    return r.json();
  }
};

let state = null;
let wastePeek = 1; // cuántas cartas del descarte se muestran (1 o hasta 3)

const SUITS = ['hearts','diamonds','clubs','spades'];
const SUIT_SYMBOL = { hearts: '♥', diamonds: '♦', clubs: '♣', spades: '♠' };
const RANK_STR = { 1:'A', 11:'J', 12:'Q', 13:'K' };

function rankNameEN(n){ if(n===1)return 'ace'; if(n===11)return 'jack'; if(n===12)return 'queen'; if(n===13)return 'king'; return String(n); }
function cardFileName(card){ return `${rankNameEN(card.rank)}_of_${card.suit}.png`; }
function cardImageUrl(card){ return `/static/assets/cards/${cardFileName(card)}`; }
function cardNameES(card){
  const ranks = {1:'As',2:'Dos',3:'Tres',4:'Cuatro',5:'Cinco',6:'Seis',7:'Siete',8:'Ocho',9:'Nueve',10:'Diez',11:'Jota',12:'Reina',13:'Rey'};
  const suits = {hearts:'Corazones',diamonds:'Diamantes',clubs:'Tréboles',spades:'Picas'};
  return `${ranks[card.rank]} de ${suits[card.suit]}`;
}
function svgDataUrlForCard(card){
  const name = cardNameES(card);
  const suit = SUIT_SYMBOL[card.suit]||'?';
  const rank = RANK_STR[card.rank]||String(card.rank);
  const color = (card.suit==='hearts'||card.suit==='diamonds')?'crimson':'#111';
  const svg = `<?xml version="1.0"?><svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 92 128'><rect x='1' y='1' rx='8' ry='8' width='90' height='126' fill='white' stroke='#333'/><text x='8' y='18' font-family='system-ui,Arial' font-size='16' fill='${color}'>${rank}</text><text x='76' y='116' font-family='system-ui,Arial' font-size='20' fill='${color}' text-anchor='end'>${suit}</text><title>${name}</title></svg>`;
  return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
}

function $(sel) { return document.querySelector(sel); }
function rankStr(n) { return RANK_STR[n] || String(n); }

function setLoading(loading) {
  const btns = document.querySelectorAll('button');
  btns.forEach(b => { b.disabled = !!loading; b.setAttribute('aria-busy', loading ? 'true' : 'false'); });
  const ov = document.getElementById('overlay'); if (ov) ov.setAttribute('aria-hidden', loading ? 'false' : 'true');
}

function toast(msg, kind = 'error') {
  const t = $('#toast');
  if (!t) return;
  t.textContent = msg;
  t.dataset.kind = kind;
  t.hidden = false;
  setTimeout(() => { t.hidden = true; t.textContent=''; }, 2000);
}

async function action(fn) {
  try {
    setLoading(true);
    await fn();
  } catch (e) {
    console.error(e);
    toast(String(e.message || e));
  } finally {
    setLoading(false);
  }
}

async function newGame() {
  await action(async () => {
    const res = await api.post('/api/game/new', { mode: 'standard', draw: 1 });
    state = res.state; render();
  });
}

async function draw() {
  await action(async () => { const res = await api.post('/api/game/move', { move: { type: 'draw' } }); state = res.state; render(); });
}
async function undo() { await action(async () => { const res = await api.post('/api/game/undo'); state = res.state; render(); }); }
async function redo() { await action(async () => { const res = await api.post('/api/game/redo'); state = res.state; render(); }); }
async function hint() { await action(async () => { const res = await api.post('/api/game/hint'); if (res.hint) highlightHint(res.hint); }); }
async function autoplay() { await action(async () => { const res = await api.post('/api/game/autoplay', { limit: 200 }); state = res.state; render(); }); }

function renderHUD() {
  $('#score').textContent = state.score;
  $('#moves').textContent = state.moves;
  $('#time').textContent = state.seconds;
  $('#draw').textContent = state.draw_count;
}

function cardEl(card) {
  const div = document.createElement('div');
  div.className = 'card' + (card.face_up ? '' : ' face-down');
  div.dataset.suit = card.suit;
  div.dataset.rank = card.rank;
  if (card.face_up) {
    const img = document.createElement('img');
    img.className = 'card-img';
    img.alt = cardNameES(card);
    img.setAttribute('aria-label', cardNameES(card));
    img.src = cardImageUrl(card);
    img.onerror = () => { img.src = svgDataUrlForCard(card); };
    div.setAttribute('role', 'img');
    div.setAttribute('aria-label', cardNameES(card));
    div.title = cardNameES(card);
    div.appendChild(img);
  }
  return div;
}

function render() {
  if (!state) return;
  renderHUD();
  // waste (mostrar 1 o peek de la anterior con offset)
  const waste = $('#waste'); waste.innerHTML = '';
  const wlen = state.waste.length;
  const visible = Math.min(wastePeek, 2, wlen);
  const start = Math.max(0, wlen - visible);
  state.waste.slice(start).forEach((c, i, arr) => {
    const el = cardEl(c);
    el.classList.add(`peek-${i}`);
    el.style.zIndex = String(100 + i);
    if (i === arr.length - 1 && c.face_up) {
      el.setAttribute('draggable', 'true');
      el.dataset.from = 'waste';
      el.addEventListener('dragstart', onDragStart);
      el.addEventListener('dblclick', onDoubleClickTop);
    }
    waste.appendChild(el);
  });
  // botón ver atrás
  const btnPeek = $('#btn-waste-peek');
  if (btnPeek) {
    btnPeek.disabled = wlen <= 1;
    btnPeek.textContent = wastePeek === 1 ? 'Ver carta anterior' : 'Ocultar';
  }
  // stock visual: mostrar dorso si hay cartas
  const stock = $('#stock');
  stock.innerHTML = '';
  if (state.stock.length) {
    const back = document.createElement('div');
    back.className = 'card face-down';
    back.setAttribute('aria-label', 'Mazo');
    stock.appendChild(back);
  } else {
    stock.textContent = '—';
  }
  // foundations
  const f = $('#foundations'); f.innerHTML='';
  for (const suit of SUITS) {
    const d = document.createElement('div'); d.className='foundation'; d.dataset.suit=suit;
    const arr = state.foundations[suit] || [];
    if (arr.length) {
      const top = arr[arr.length - 1];
      const el = cardEl(top);
      d.appendChild(el);
    } else {
      d.textContent = SUIT_SYMBOL[suit] || '';
    }
    d.addEventListener('dragover', e => { e.preventDefault(); d.classList.add('droptarget'); });
    d.addEventListener('dragleave', () => d.classList.remove('droptarget'));
    d.addEventListener('drop', onDropFoundation);
    f.appendChild(d);
  }
  // tableau
  const tab = $('#tableau'); tab.innerHTML='';
  state.tableau.forEach((col, i) => {
    const d = document.createElement('div'); d.className='col'; d.dataset.col = String(i);
    col.forEach((c, j) => {
      const el = cardEl(c);
      el.dataset.index = String(j);
      // Permitir arrastrar cualquier carta boca arriba (para cadenas)
      if (c.face_up) {
        el.setAttribute('draggable', 'true');
        el.addEventListener('dragstart', onDragStart);
      }
      // Doble clic sobre la carta superior de la columna => t2f
      if (j === col.length - 1 && c.face_up) {
        el.addEventListener('dblclick', onDoubleClickTop);
      }
      d.appendChild(el);
    });
    d.addEventListener('dragover', e => { e.preventDefault(); d.classList.add('droptarget'); });
    d.addEventListener('dragleave', () => d.classList.remove('droptarget'));
    d.addEventListener('drop', onDropTableau);
    tab.appendChild(d);
  });
}

function onDragStart(e) {
  const el = e.target;
  const parent = el.parentElement;
  const fromWaste = el.dataset.from === 'waste' || parent.id === 'waste';
  if (fromWaste) {
    e.dataTransfer.setData('text/plain', JSON.stringify({ from: 'waste' }));
    return;
  }
  const from_col = Number(parent.dataset.col);
  const start_index = Number(el.dataset.index);
  e.dataTransfer.setData('text/plain', JSON.stringify({ from: 'tableau', from_col, start_index }));
}

async function onDropTableau(e) {
  e.preventDefault();
  const to_col = Number(e.currentTarget.dataset.col);
  const data = JSON.parse(e.dataTransfer.getData('text/plain'));
  let move;
  if (data.from === 'waste') {
    move = { type: 'w2t', to_col };
  } else {
    move = { type: 't2t', from_col: data.from_col, start_index: data.start_index, to_col };
  }
  await action(async () => {
    const res = await api.post('/api/game/move', { move });
    state = res.state; render();
  });
}

async function onDropFoundation(e) {
  e.preventDefault();
  const data = JSON.parse(e.dataTransfer.getData('text/plain'));
  let move;
  if (data.from === 'waste') {
    move = { type: 'w2f' };
  } else {
    // Solo válido si arrastramos la carta superior de la columna
    const topLen = state.tableau[data.from_col].length;
    if (data.start_index !== topLen - 1) {
      e.currentTarget.classList.add('invalid');
      setTimeout(() => e.currentTarget.classList.remove('invalid'), 400);
      return;
    }
    move = { type: 't2f', from_col: data.from_col };
  }
  await action(async () => {
    const res = await api.post('/api/game/move', { move });
    state = res.state; render();
  });
}

async function onDoubleClickTop(e) {
  const el = e.currentTarget;
  const parent = el.parentElement;
  if (parent.id === 'waste') {
    await action(async () => { const res = await api.post('/api/game/move', { move: { type: 'w2f' } }); state = res.state; render(); });
  } else if (parent.classList.contains('col')) {
    const from_col = Number(parent.dataset.col);
    const idx = Number(el.dataset.index);
    if (idx !== state.tableau[from_col].length - 1) return; // solo tope
    await action(async () => { const res = await api.post('/api/game/move', { move: { type: 't2f', from_col } }); state = res.state; render(); });
  }
}

function highlightHint(h) {
  if (!h) return;
  if (h.type === 'draw') { $('#btn-draw').classList.add('droptarget'); setTimeout(() => $('#btn-draw').classList.remove('droptarget'), 600); return; }
  if (h.type === 'w2f' || h.type === 'w2t') { $('#waste').classList.add('droptarget'); setTimeout(() => $('#waste').classList.remove('droptarget'), 600); return; }
  if (h.type === 't2f' || h.type === 't2t') { const sel = h.from_col != null ? `.col[data-col="${h.from_col}"]` : '.col'; const col = document.querySelector(sel); if (col) { col.classList.add('droptarget'); setTimeout(() => col.classList.remove('droptarget'), 600);} }
}

// controls
document.getElementById('btn-new').addEventListener('click', newGame);
document.getElementById('btn-draw').addEventListener('click', draw);
document.getElementById('btn-undo').addEventListener('click', undo);
document.getElementById('btn-redo').addEventListener('click', redo);
document.getElementById('btn-hint').addEventListener('click', hint);
document.getElementById('btn-autoplay').addEventListener('click', autoplay);

document.getElementById('stock').addEventListener('click', draw);
document.getElementById('stock').addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') draw(); });

// waste peek toggle
const peekBtn = document.getElementById('btn-waste-peek');
if (peekBtn) {
  peekBtn.addEventListener('click', () => {
    wastePeek = wastePeek === 1 ? Math.min(3, (state?.waste?.length || 0)) : 1;
    render();
  });
}

// bootstrap
api.get('/api/game/state').then(s => { state = s; render(); }).catch(newGame);
