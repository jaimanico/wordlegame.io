// static/script.js - defensive and clear UX
let gameId = null;
let guesses = [];
let attemptsLeft = 6;
let wordLength = 5;

const startBtn = document.getElementById('startBtn');
const playerName = document.getElementById('playerName');
const board = document.getElementById('board');
const gameInfo = document.getElementById('gameInfo');
const gameTitle = document.getElementById('gameTitle');
const statusLine = document.getElementById('statusLine');
const guessForm = document.getElementById('guessForm');
const guessInput = document.getElementById('guessInput');
const guessBtn = document.getElementById('guessBtn');
const messageEl = document.getElementById('message');

startBtn.addEventListener('click', startGame);
guessBtn.addEventListener('click', submitGuess);
guessInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') submitGuess(); });

function showMessage(text, isError=false){
  messageEl.textContent = text || '';
  messageEl.classList.toggle('error', !!isError);
}

async function startGame(){
  showMessage('');
  const player = (playerName.value || 'guest').trim();
  try {
    const res = await fetch('/api/start', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ player })
    });
    const data = await safeJson(res);
    if (!res.ok){
      showMessage(`Could not start game: ${data?.error || res.statusText}`, true);
      return;
    }

    // defensive defaults if backend shape differs
    gameId = data.game_id ?? data.id ?? null;
    guesses = Array.isArray(data.guesses) ? data.guesses : [];
    wordLength = data.word_length || 5;
    attemptsLeft = data.attempts_left ?? 6;

    gameInfo.hidden = false;
    guessForm.hidden = false;
    gameTitle.textContent = `Game ${gameId ?? ''}`;
    updateStatus();
    renderBoard();
    guessInput.value = '';
    guessInput.focus();
  } catch(err){
    showMessage('Network error starting game', true);
    console.error(err);
  }
}

async function submitGuess(){
  showMessage('');
  if (!gameId){
    showMessage('Start a game first', true);
    return;
  }
  const raw = (guessInput.value || '').trim().toUpperCase();
  if (raw.length !== wordLength){
    showMessage(`Guess must be ${wordLength} letters`, true);
    return;
  }
  // disable UI briefly
  guessBtn.disabled = true;
  guessInput.disabled = true;

  try {
    const res = await fetch('/api/guess', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ game_id: gameId, guess: raw })
    });
    const data = await safeJson(res);
    if (!res.ok){
      showMessage(data?.error || `Server error: ${res.status}`, true);
      console.error('bad response', data);
      return;
    }

    // Ensure guesses is an array (defensive)
    if (!Array.isArray(data.guesses)){
      // if server returns only words array, accept that shape too
      if (Array.isArray(data) || Array.isArray(data.words)) {
        guesses = Array.isArray(data) ? data : data.words;
      } else {
        guesses = [];
      }
    } else {
      guesses = data.guesses;
    }

    attemptsLeft = data.attempts_left ?? attemptsLeft;
    renderBoard();
    updateStatus();

    if (data.is_won){
      showMessage('🎉 You won! Start a new game to play again.');
      guessForm.hidden = true;
    } else if (attemptsLeft <= 0){
      showMessage(`Game over. The word was ${data.target_word || 'unknown'}`);
      guessForm.hidden = true;
    } else {
      guessInput.value = '';
      guessInput.focus();
    }
  } catch (err){
    console.error(err);
    showMessage('Network error submitting guess', true);
  } finally {
    guessBtn.disabled = false;
    guessInput.disabled = false;
  }
}

function updateStatus(){
  statusLine.textContent = `Attempts left: ${attemptsLeft}`;
}

function renderBoard(){
  board.innerHTML = '';
  // We expect guesses to be an array of objects like:
  // { word: "PLAYS", feedback: ["absent","present","correct","absent","absent"] }
  // But be defensive if server returns strings.

  // Show rows equal to attempts (6 default)
  const maxRows = 6;
  for (let r = 0; r < maxRows; r++){
    const rowEl = document.createElement('div');
    rowEl.className = 'row';
    if (r < guesses.length){
      const g = guesses[r];
      // normalize
      let letters = [];
      let feedback = [];
      if (typeof g === 'string'){
        letters = g.toUpperCase().split('');
        feedback = Array(wordLength).fill('absent');
      } else {
        letters = (g.word || '').toUpperCase().split('');
        feedback = Array.isArray(g.feedback) ? g.feedback : Array(wordLength).fill('absent');
      }
      // pad letters
      while (letters.length < wordLength) letters.push('');
      for (let i = 0; i < wordLength; i++){
        const tile = createTile(letters[i] || '', feedback[i]);
        rowEl.appendChild(tile);
      }
    } else {
      // empty row
      for (let i = 0; i < wordLength; i++){
        const tile = createTile('', 'empty');
        rowEl.appendChild(tile);
      }
    }
    board.appendChild(rowEl);
  }
}

function createTile(letter, feedback){
  const t = document.createElement('div');
  t.className = 'tile';
  if (feedback === 'correct') t.classList.add('correct');
  else if (feedback === 'present') t.classList.add('present');
  else if (feedback === 'absent') t.classList.add('absent');
  t.textContent = letter || '';
  return t;
}

// safe JSON parser that won't throw when server returns no json
async function safeJson(response){
  try {
    const txt = await response.text();
    if (!txt) return {};
    return JSON.parse(txt);
  } catch(err){
    console.warn('Response not JSON', err);
    return {};
  }
}
