let GAME_ID = null;

async function post(url, body={}){
  const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  return r.json();
}

function suitSymbol(s){ return {hearts:'♥', diamonds:'♦', clubs:'♣', spades:'♠'}[s]; }

function renderCard(node, card, offset=0){
  const el = document.createElement('div');
  el.className = 'card ' + (card.face_up ? '' : 'face-down') + ' ' + (['hearts','diamonds'].includes(card.suit) ? 'red':'black');
  el.style.top = offset+'px';
  el.textContent = card.face_up ? (card.rank + suitSymbol(card.suit)) : '';
  node.appendChild(el);
}

function render(){
  // no-op
}

function renderState({tableau, foundations, stock, waste, moves, game_won}){
  document.getElementById('moves').textContent = 'Movimientos: ' + (moves ?? 0);

  // Stock
  const stockEl = document.getElementById('stock');
  stockEl.innerHTML = '';
  if (stock > 0){
    renderCard(stockEl, {face_up:false, suit:'spades', rank:'X'});
  }

  // Waste
  const wasteEl = document.getElementById('waste');
  wasteEl.innerHTML = '';
  if (waste && waste.length){
    const top = waste[waste.length-1];
    renderCard(wasteEl, top);
  }

  // Foundations
  for (const s of ['hearts','diamonds','clubs','spades']){
    const fEl = document.getElementById('foundation-'+s);
    fEl.innerHTML = '';
    const arr = foundations[s] || [];
    if (arr.length){
      renderCard(fEl, arr[arr.length-1]);
    }
  }

  // Tableau
  for (let i=0;i<7;i++){
    const tEl = document.getElementById('tableau-'+i);
    tEl.innerHTML = '';
    const pile = tableau[i] || [];
    let y = 0;
    for (const c of pile){
      renderCard(tEl, c, y);
      y += (c.face_up ? 28 : 18);
    }
  }

  document.getElementById('win-banner').classList.toggle('hidden', !game_won);
}

async function newGame(){
  const data = await post('/new_game');
  GAME_ID = data.game_id;
  renderState(data);
}

async function draw(){
  if (!GAME_ID) return;
  const data = await post('/draw_card', {game_id: GAME_ID});
  // Patch stock/waste + small refresh
  const state = await post('/get_game_state', {game_id: GAME_ID});
  renderState(state);
}

async function hint(){
  if (!GAME_ID) return;
  const {move} = await post('/hint', {game_id: GAME_ID});
  if (!move){ alert('Sin movimientos obvios.'); return; }
  alert('Sugerencia: ' + JSON.stringify(move));
}

async function undo(){
  if (!GAME_ID) return;
  const data = await post('/undo', {game_id: GAME_ID});
  renderState(data);
}

async function saveGame(){
  if (!GAME_ID) return;
  const name = prompt('Nombre de guardado:');
  if (!name) return;
  await post('/save_game', {game_id: GAME_ID, name});
  alert('Guardado.');
}

async function loadGame(){
  const name = prompt('Nombre a cargar (usa /list_saves para ver):');
  if (!name) return;
  const data = await post('/load_game', {name});
  GAME_ID = data.game_id;
  renderState(data);
}

document.getElementById('new-game-btn').addEventListener('click', newGame);
document.getElementById('draw-btn').addEventListener('click', draw);
document.getElementById('hint-btn').addEventListener('click', hint);
document.getElementById('undo-btn').addEventListener('click', undo);
document.getElementById('save-btn').addEventListener('click', saveGame);
document.getElementById('load-btn').addEventListener('click', loadGame);

newGame();
