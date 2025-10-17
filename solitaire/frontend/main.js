// Improved SPA logic: better rendering, drag/drop and double-click helpers.
const api = {
  post: (url, body) => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) }).then(r => r.json()),
  get: (url) => fetch(url).then(r => r.json())
};

let state = null;

const SUITS = ['hearts','diamonds','clubs','spades'];
const SUIT_SYMBOL = { hearts: '♥', diamonds: '♦', clubs: '♣', spades: '♠' };
const RANK_STR = { 1:'A', 11:'J', 12:'Q', 13:'K' };

function $(sel) { return document.querySelector(sel); }
function rankStr(n) { return RANK_STR[n] || String(n); }

async function newGame() {
  const res = await api.post('/api/game/new', { mode: 'standard', draw: 1 });
  state = res.state; render();
}

async function draw() { const res = await api.post('/api/game/move', { move: { type: 'draw' } }); state = res.state; render(); }
async function undo() { try { const res = await api.post('/api/game/undo'); state = res.state; render(); } catch {} }
async function redo() { try { const res = await api.post('/api/game/redo'); state = res.state; render(); } catch {} }
async function hint() { const res = await api.post('/api/game/hint'); if (res.hint) highlightHint(res.hint); }
async function autoplay() { const res = await api.post('/api/game/autoplay', { limit: 200 }); state = res.state; render(); }

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
    const r = document.createElement('span'); r.className='rank'; r.textContent = rankStr(card.rank);
    const s = document.createElement('span'); s.className='suit'; s.textContent = SUIT_SYMBOL[card.suit] || '?';
    if (card.suit === 'hearts' || card.suit === 'diamonds') { div.style.color = 'crimson'; }
    div.appendChild(r); div.appendChild(s);
  }
  return div;
}

function render() {
  if (!state) return;
  renderHUD();
  // waste (solo la carta superior es arrastrable)
  const waste = $('#waste'); waste.innerHTML = '';
  state.waste.forEach((c, idx, arr) => {
    const el = cardEl(c);
    if (idx === arr.length - 1 && c.face_up) {
      el.setAttribute('draggable', 'true');
      el.dataset.from = 'waste';
      el.addEventListener('dragstart', onDragStart);
      el.addEventListener('dblclick', onDoubleClickTop);
    }
    waste.appendChild(el);
  });
  // stock visual
  const stock = $('#stock'); stock.textContent = state.stock.length ? '🂠' : '×';
  // foundations
  const f = $('#foundations'); f.innerHTML='';
  for (const suit of SUITS) {
    const d = document.createElement('div'); d.className='foundation'; d.dataset.suit=suit;
    const arr = state.foundations[suit] || [];
    d.textContent = arr.length ? (rankStr(arr[arr.length-1].rank) + ' ' + (SUIT_SYMBOL[suit]||'')) : (SUIT_SYMBOL[suit]||'');
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
  const res = await api.post('/api/game/move', { move });
  state = res.state; render();
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
  const res = await api.post('/api/game/move', { move });
  state = res.state; render();
}

async function onDoubleClickTop(e) {
  const el = e.currentTarget;
  const parent = el.parentElement;
  if (parent.id === 'waste') {
    const res = await api.post('/api/game/move', { move: { type: 'w2f' } });
    state = res.state; render();
  } else if (parent.classList.contains('col')) {
    const from_col = Number(parent.dataset.col);
    const idx = Number(el.dataset.index);
    if (idx !== state.tableau[from_col].length - 1) return; // solo tope
    const res = await api.post('/api/game/move', { move: { type: 't2f', from_col } });
    state = res.state; render();
  }
}

function highlightHint(h) {
  if (!h) return;
  if (h.type === 'draw') { $('#btn-draw').classList.add('droptarget'); setTimeout(() => $('#btn-draw').classList.remove('droptarget'), 600); return; }
  if (h.type === 'w2f' || h.type === 'w2t') { $('#waste').classList.add('droptarget'); setTimeout(() => $('#waste').classList.remove('droptarget'), 600); return; }
  if (h.type === 't2f' || h.type === 't2t') { const sel = h.from_col != null ? `.col[data-col="${h.from_col}"]` : '.col'; const col = document.querySelector(sel); if (col) { col.classList.add('droptarget'); setTimeout(() => col.classList.remove('droptarget'), 600);} }
}

document.getElementById('btn-new').addEventListener('click', newGame);
document.getElementById('btn-draw').addEventListener('click', draw);
document.getElementById('btn-undo').addEventListener('click', undo);
document.getElementById('btn-redo').addEventListener('click', redo);
document.getElementById('btn-hint').addEventListener('click', hint);
document.getElementById('btn-autoplay').addEventListener('click', autoplay);

document.getElementById('stock').addEventListener('click', draw);
document.getElementById('stock').addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') draw(); });

// bootstrap
api.get('/api/game/state').then(s => { state = s; render(); }).catch(newGame);

