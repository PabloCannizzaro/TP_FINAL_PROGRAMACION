// Minimal SPA logic: render state, handle clicks and drag moves.
const api = {
  post: (url, body) => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) }).then(r => r.json()),
  get: (url) => fetch(url).then(r => r.json())
};

let state = null;

const SUIT_SYMBOL = { hearts: '♥', diamonds: '♦', clubs: '♣', spades: '♠' };
const RANK_STR = { 1:'A', 11:'J', 12:'Q', 13:'K' };

function rankStr(n) { return RANK_STR[n] || String(n); }

async function newGame() {
  const res = await api.post('/api/game/new', { mode: 'standard', draw: 1 });
  state = res.state;
  render();
}

async function draw() {
  const res = await api.post('/api/game/move', { move: { type: 'draw' } });
  state = res.state; render();
}

async function undo() {
  try { const res = await api.post('/api/game/undo'); state = res.state; render(); } catch {}
}
async function redo() {
  try { const res = await api.post('/api/game/redo'); state = res.state; render(); } catch {}
}
async function hint() {
  const res = await api.post('/api/game/hint');
  if (res.hint) {
    highlightHint(res.hint);
  }
}
async function autoplay() {
  const res = await api.post('/api/game/autoplay', { limit: 200 });
  state = res.state; render();
}

function $(sel) { return document.querySelector(sel); }

function renderHUD() {
  $('#score').textContent = state.score;
  $('#moves').textContent = state.moves;
  $('#time').textContent = state.seconds;
  $('#draw').textContent = state.draw_count;
}

function cardEl(card) {
  const div = document.createElement('div');
  div.className = 'card' + (card.face_up ? '' : ' face-down');
  div.setAttribute('draggable', card.face_up ? 'true' : 'false');
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
  // waste
  const waste = $('#waste'); waste.innerHTML = '';
  state.waste.forEach(c => waste.appendChild(cardEl(c)));
  // stock
  const stock = $('#stock'); stock.textContent = state.stock.length ? '🂠' : '↺';
  // foundations
  const f = $('#foundations'); f.innerHTML='';
  for (const suit of ['hearts','diamonds','clubs','spades']) {
    const d = document.createElement('div'); d.className='foundation'; d.dataset.suit=suit;
    const arr = state.foundations[suit] || [];
    d.textContent = arr.length ? (rankStr(arr[arr.length-1].rank) + ' ' + (SUIT_SYMBOL[suit]||'')) : (SUIT_SYMBOL[suit]||'');
    f.appendChild(d);
  }
  // tableau
  const tab = $('#tableau'); tab.innerHTML='';
  state.tableau.forEach((col, i) => {
    const d = document.createElement('div'); d.className='col'; d.dataset.col = String(i);
    col.forEach((c, j) => {
      const el = cardEl(c);
      el.dataset.index = String(j);
      el.addEventListener('dragstart', onDragStart);
      d.appendChild(el);
    });
    d.addEventListener('dragover', e => { e.preventDefault(); d.classList.add('droptarget'); });
    d.addEventListener('dragleave', () => d.classList.remove('droptarget'));
    d.addEventListener('drop', onDrop);
    tab.appendChild(d);
  });
}

function onDragStart(e) {
  const el = e.target;
  const from_col = Number(el.parentElement.dataset.col);
  const start_index = Number(el.dataset.index);
  e.dataTransfer.setData('text/plain', JSON.stringify({ from_col, start_index }));
}

async function onDrop(e) {
  e.preventDefault();
  const to_col = Number(e.currentTarget.dataset.col);
  const data = JSON.parse(e.dataTransfer.getData('text/plain'));
  const res = await api.post('/api/game/move', { move: { type: 't2t', from_col: data.from_col, start_index: data.start_index, to_col } });
  state = res.state; render();
}

function highlightHint(h) {
  if (!h) return;
  // naive visual hint: flash controls or column borders
  if (h.type === 'draw') { $('#btn-draw').classList.add('droptarget'); setTimeout(() => $('#btn-draw').classList.remove('droptarget'), 600); return; }
  if (h.type === 'w2f' || h.type === 'w2t') { $('#waste').classList.add('droptarget'); setTimeout(() => $('#waste').classList.remove('droptarget'), 600); return; }
  if (h.type === 't2f') { const col = document.querySelector(`.col[data-col="${h.from_col}"]`); if (col) { col.classList.add('droptarget'); setTimeout(() => col.classList.remove('droptarget'), 600);} }
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

