// static/script.js - robust UI + defensive normalization
let gameId = null;
let guesses = [];
let attemptsLeft = 6;
let wordLength = 5;
window.__target_word_for_ui = null; // small cache for revealed solution

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
const endScreen = document.getElementById('endScreen');
const endTitle = document.getElementById('endTitle');
const endSubtitle = document.getElementById('endSubtitle');
const endWord = document.getElementById('endWord');
const restartBtn = document.getElementById('restartBtn');

startBtn.addEventListener('click', startGame);
guessBtn.addEventListener('click', submitGuess);
guessInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') submitGuess(); });
if (restartBtn) {
  restartBtn.addEventListener('click', handleRestart);
}

// ------------------- helpers -------------------

// normalize any guess entry into { word: "ABCDE", feedback: ["correct","present","absent", ...] }
// normalize any guess entry into { word: "ABCDE", feedback: ["correct","present","absent", ...] }
function normalizeGuessEntry(raw, wordLength = 5) {
  if (!raw) return { word: "", feedback: Array(wordLength).fill("absent") };

  // If raw is a plain string
  if (typeof raw === "string") {
    return { word: raw.toUpperCase(), feedback: Array(wordLength).fill("absent") };
  }

  // Extract word-like fields
  const word = (raw.word || raw.guess || raw.text || raw.answer || raw.value || "").toString().toUpperCase();

  // Candidate feedback fields (could be string, array, numbers, objects)
  let fb = raw.feedback ?? raw.result ?? raw.statuses ?? raw.status ?? raw.states ?? raw.codes ?? null;

  // letters array shape: [{char, status}, ...]
  if (!fb && Array.isArray(raw.letters)) {
    fb = raw.letters.map(l => l.status || l.state || l.flag || null);
  }

  // If fb is a string (e.g. "GYBGB" or "gYbGb"), convert it to tokens
  if (typeof fb === "string") {
    const tokens = fb.split("").map(ch => {
      if (ch === "G" || ch === "g") return "correct";
      if (ch === "Y" || ch === "y") return "present";
      // support B, b, 0 as absent markers too
      return "absent";
    });
    fb = tokens;
  }

  // Numeric codes like 2=correct,1=present,0=absent
  if (Array.isArray(fb) && fb.length && typeof fb[0] === "number") {
    fb = fb.map(n => (n === 2 ? "correct" : n === 1 ? "present" : "absent"));
  }

  // If fb is array of objects like [{status:"correct"}]
  if (Array.isArray(fb) && fb.length && typeof fb[0] === "object") {
    fb = fb.map(x => x.status || x.state || x.flag || "absent");
  }

  // Final safety: ensure array of correct length
  if (!Array.isArray(fb)) fb = Array(wordLength).fill("absent");
  while (fb.length < wordLength) fb.push("absent");
  if (fb.length > wordLength) fb = fb.slice(0, wordLength);

  // Normalize token names
  fb = fb.map(s => {
    if (!s) return "absent";
    s = s.toString().toLowerCase();
    if (s === "g" || s === "green" || s === "correct") return "correct";
    if (s === "y" || s === "yellow" || s === "present") return "present";
    if (s === "a" || s === "absent" || s === "grey" || s === "gray") return "absent";
    if (s.includes("correct")) return "correct";
    if (s.includes("present") || s.includes("yellow")) return "present";
    return "absent";
  });

  const out = { word: word || "", feedback: fb };

  return out;
}

function showMessage(text, isError = false) {
  messageEl.textContent = text || '';
  messageEl.classList.toggle('error', !!isError);
}

function updateStatus() {
  statusLine.textContent = `Attempts left: ${attemptsLeft}`;
}

function hideEndScreen() {
  if (!endScreen) return;
  endScreen.classList.remove('visible');
  endScreen.setAttribute('aria-hidden', 'true');
}

function showEndScreen({ won, word }) {
  if (!endScreen) return;
  endTitle.textContent = won ? 'You cracked it!' : 'Game over';
  endSubtitle.textContent = won
    ? 'Nice job. Ready for another round?'
    : 'Better luck next time. Want to try again?';
  endWord.textContent = word ? `The word was ${word}` : '';
  endScreen.classList.add('visible');
  endScreen.setAttribute('aria-hidden', 'false');
}

// safe JSON parser that won't throw when server returns no json
async function safeJson(response) {
  try {
    const txt = await response.text();
    if (!txt) return {};
    return JSON.parse(txt);
  } catch (err) {
    console.warn('Response not JSON', err);
    return {};
  }
}

// ------------------- UI rendering -------------------

function createTile(letter, feedback) {
  const t = document.createElement('div');
  t.className = 'tile';
  if (feedback === 'correct') t.classList.add('correct');
  else if (feedback === 'present') t.classList.add('present');
  else if (feedback === 'absent') t.classList.add('absent');
  t.textContent = (letter || '').toString().toUpperCase();
  return t;
}

function renderBoard() {
  const board = document.getElementById("board");
  board.innerHTML = "";

  // Create 6 rows (for 6 attempts)
  for (let rowIndex = 0; rowIndex < 6; rowIndex++) {
    const row = document.createElement("div");
    row.classList.add("row");

    for (let colIndex = 0; colIndex < wordLength; colIndex++) {
      const tile = document.createElement("div");
      tile.classList.add("tile");
      
      // If we have a guess for this row, populate it
      if (guesses[rowIndex]) {
        const guess = normalizeGuessEntry(guesses[rowIndex], wordLength);
        tile.textContent = guess.word[colIndex] || "";
        
        // Apply color classes based on feedback
        if (guess.feedback && guess.feedback[colIndex]) {
          tile.classList.add(guess.feedback[colIndex]);
        }
      }
      
      row.appendChild(tile);
    }
    board.appendChild(row);
  }
}

// ------------------- API actions -------------------

async function startGame() {
  showMessage('');
  hideEndScreen();
  const player = (playerName.value || 'guest').trim();
  startBtn.disabled = true;

  try {
    const res = await fetch('/api/games', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player })
    });
    const data = await safeJson(res);

    if (!res.ok) {
      showMessage(`Could not start game: ${data?.error || res.statusText}`, true);
      console.error('start failed', data);
      return;
    }

    // clear cached target when starting fresh
    window.__target_word_for_ui = null;

    // Accept multiple shapes
    const gamePayload = data.game ?? data;
    gameId = data.game_id ?? data.id ?? (gamePayload && (gamePayload.id ?? gamePayload.game_id)) ?? null;

    guesses = Array.isArray(data.guesses) ? data.guesses :
              (Array.isArray(gamePayload?.guesses) ? gamePayload.guesses : []);

    wordLength = data.word_length ?? gamePayload?.word_length ?? 5;

    // Backend tracks attempts and max_attempts; derive attemptsLeft here
    const maxAttemptsStart = gamePayload?.max_attempts ?? 6;
    const attemptsUsedStart = gamePayload?.attempts ?? 0;
    attemptsLeft = Math.max(0, maxAttemptsStart - attemptsUsedStart);

    gameInfo.hidden = false;
    guessForm.hidden = false;
    gameTitle.textContent = `Game ${gameId ?? ''}`;
    updateStatus();
    renderBoard();
    guessInput.value = '';
    guessInput.focus();
  } catch (err) {
    console.error(err);
    showMessage('Network error starting game', true);
  } finally {
    startBtn.disabled = false;
  }
}
function updateBoard() {
  const board = document.getElementById('board');
  board.innerHTML = '';

  for (const g of guesses) {
    const normalized = normalizeGuessEntry(g, wordLength);
    const row = document.createElement('div');
    row.classList.add('row');

    normalized.feedback.forEach((status, i) => {
      const tile = document.createElement('div');
      tile.classList.add('tile');
      tile.textContent = normalized.word[i] || '';
      // add color class
      if (status) tile.classList.add(status.toLowerCase());
      row.appendChild(tile);
    });

    board.appendChild(row);
  }
}

async function submitGuess() {
  showMessage('');
  if (!gameId) {
    showMessage('Start a game first', true);
    return;
  }

  const raw = (guessInput.value || '').trim().toUpperCase();
  if (raw.length !== wordLength) {
    showMessage(`Guess must be ${wordLength} letters`, true);
    return;
  }

  guessBtn.disabled = true;
  guessInput.disabled = true;

  try {
    const res = await fetch(`/api/games/${encodeURIComponent(gameId)}/guess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ guess: raw })
    });
    const data = await safeJson(res);

    if (!res.ok) {
      showMessage(data?.error || `Server error: ${res.status}`, true);
      console.error('guess failed', data);
      return;
    }

    const gamePayload = data.game ?? data;

    // Normalize guesses array from different shapes:
    if (Array.isArray(data.guesses)) {
      guesses = data.guesses;
    } else if (Array.isArray(gamePayload?.guesses)) {
      guesses = gamePayload.guesses;
    } else if (Array.isArray(data)) {
      guesses = data;
    } else {
      // fallback: append last guessed word with no feedback (normalized later)
      guesses.push({ word: raw, feedback: Array(wordLength).fill('absent') });
    }

    // Derive attemptsLeft from gamePayload.attempts / max_attempts when available
    const maxAttempts = gamePayload?.max_attempts ?? 6;
    const attemptsUsed = gamePayload?.attempts ?? guesses.length ?? 0;
    attemptsLeft = Math.max(0, maxAttempts - attemptsUsed);

    // If backend returned a revealed target, cache it
    const targetWord = (data.target_word ?? data.target ?? data.solution ?? data.answer ?? data.game?.target_word ?? null);
    if (targetWord) window.__target_word_for_ui = targetWord.toString().toUpperCase();

    renderBoard();
    updateStatus();

    const won = (data.won ?? gamePayload?.won) === true;

    if (won) {
      const finalWord = window.__target_word_for_ui || guesses.at(-1)?.word || raw;
      showMessage(`🎉 You won! The word was ${finalWord}`);
      guessForm.hidden = true;
      showEndScreen({ won: true, word: finalWord });
    } else if (attemptsLeft <= 0) {
      // Try to fetch final target from backend if not provided
      let finalTarget = window.__target_word_for_ui;
      if (!finalTarget && gameId) {
        try {
          const infoRes = await fetch(`/api/games/${encodeURIComponent(gameId)}`);
          const infoJson = await safeJson(infoRes);
          finalTarget = infoJson.target_word ?? infoJson.target ?? infoJson.answer ?? infoJson.solution ?? infoJson.game?.target_word ?? null;
          if (finalTarget) finalTarget = finalTarget.toString().toUpperCase();
        } catch (err) {
          console.warn('Could not fetch final target', err);
        }
      }

      if (finalTarget) {
        showMessage(`Game over. The word was ${finalTarget}`);
      } else {
        showMessage('Game over. The word was unknown');
      }
      guessForm.hidden = true;
      showEndScreen({ won: false, word: finalTarget });
    } else {
      // continue play
      guessInput.value = '';
      guessInput.focus();
    }
  } catch (err) {
    console.error(err);
    showMessage('Network error submitting guess', true);
  } finally {
    guessBtn.disabled = false;
    guessInput.disabled = false;
  }
}

async function handleRestart() {
  // Clear current state and start a fresh game for the same player
  guesses = [];
  attemptsLeft = 6;
  wordLength = 5;
  board.innerHTML = '';
  showMessage('');
  hideEndScreen();
  await startGame();
}
