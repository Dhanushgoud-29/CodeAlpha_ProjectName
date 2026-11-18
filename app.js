/**
 * Hangman Pro — Web Dashboard Edition
 * CodeAlpha Python Internship Task 1
 */

// ==============================================================================
// 1. DATA & CONSTANTS
// ==============================================================================

const MAX_MISTAKES = 6;

const CATEGORIES = {
  Programming: [
    { word: "python", hint: "A popular interpreted language named after Monty Python" },
    { word: "hangman", hint: "The classic word-guessing game you are playing right now" },
    { word: "developer", hint: "A creative professional who builds software applications" },
    { word: "keyboard", hint: "Hardware peripheral used to type characters and commands" },
    { word: "programming", hint: "The craft of writing instructions for computers to execute" },
    { word: "variable", hint: "A named storage location in memory holding data values" },
    { word: "algorithm", hint: "A finite sequence of well-defined steps to solve a problem" },
    { word: "terminal", hint: "A text-based window used to run shell commands" },
    { word: "function", hint: "A reusable block of code designed to perform a single action" },
    { word: "database", hint: "An organized collection of data stored electronically" }
  ],
  Animals: [
    { word: "dolphin", hint: "Highly intelligent aquatic mammal famous for echolocation" },
    { word: "elephant", hint: "The largest living land animal, recognized by its long trunk" },
    { word: "penguin", hint: "Flightless bird thriving in Antarctic regions" },
    { word: "cheetah", hint: "The fastest land animal on Earth capable of high-speed sprints" },
    { word: "kangaroo", hint: "Australian marsupial known for powerful bounding hops" },
    { word: "octopus", hint: "Eight-armed marine mollusk with extraordinary camouflage skills" },
    { word: "giraffe", hint: "The tallest living terrestrial animal with an elongated neck" }
  ],
  Countries: [
    { word: "canada", hint: "Second-largest country by land area, home of the maple leaf" },
    { word: "brazil", hint: "Largest nation in South America, famous for the Amazon and football" },
    { word: "japan", hint: "East Asian island nation famed for cherry blossoms and technology" },
    { word: "egypt", hint: "Ancient civilization centered along the fertile banks of the Nile" },
    { word: "germany", hint: "European economic powerhouse famous for precision engineering" },
    { word: "australia", hint: "Vast island continent famous for the Great Barrier Reef" }
  ],
  Science: [
    { word: "gravity", hint: "Fundamental force pulling mass toward the center of planets" },
    { word: "galaxy", hint: "Vast cosmic system of stars, stellar remnants, and dark matter" },
    { word: "molecule", hint: "The smallest fundamental unit of a chemical compound" },
    { word: "photosynthesis", hint: "Biological process converting light into chemical energy" },
    { word: "telescope", hint: "Optical instrument enabling observation of distant celestial bodies" },
    { word: "quantum", hint: "The minimum amount of any physical entity involved in an interaction" }
  ]
};

const HANGMAN_PARTS = [
  "partHead",
  "partTorso",
  "partLeftArm",
  "partRightArm",
  "partLeftLeg",
  "partRightLeg"
];

const KEYBOARD_LAYOUT = [
  ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
  ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
  ["Z", "X", "C", "V", "B", "N", "M"]
];

// ==============================================================================
// 2. STATE MANAGEMENT
// ==============================================================================

let currentCategory = "Programming";
let secretWord = "";
let currentHint = "";
let guessedLetters = new Set();
let guessHistory = []; // Chronological list of { letter, isCorrect } in current round
let incorrectGuesses = 0;
let hintRevealed = false;
let isGameOver = false;
let soundEnabled = true;

// Persistent Statistics
let stats = {
  games: 0,
  wins: 0,
  losses: 0,
  streak: 0,
  bestStreak: 0
};

// Persistent Match History
let matchHistory = [];
try {
  const savedHistory = localStorage.getItem("hangman_match_history");
  if (savedHistory) matchHistory = JSON.parse(savedHistory);
} catch (e) {
  console.warn("Could not read localStorage match history", e);
}

// Load saved stats
try {
  const saved = localStorage.getItem("hangman_stats");
  if (saved) stats = JSON.parse(saved);
} catch (e) {
  console.warn("Could not read localStorage stats", e);
}

function saveStats() {
  try {
    localStorage.setItem("hangman_stats", JSON.stringify(stats));
  } catch (e) {
    console.warn("Could not save stats", e);
  }
}

// ==============================================================================
// 3. SOUND SYNTHESIZER (Web Audio API - Non-blocking Safe)
// ==============================================================================

let audioCtx = null;

function getAudioContext() {
  try {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) audioCtx = new AudioContextClass();
    }
    if (audioCtx && audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    return audioCtx;
  } catch (e) {
    return null;
  }
}

function playTone(freq, type, duration, delay = 0) {
  if (!soundEnabled) return;
  const ctx = getAudioContext();
  if (!ctx) return;

  setTimeout(() => {
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (err) {
      // Audio autoplay policy catch
    }
  }, delay * 1000);
}

function playSound(name) {
  try {
    switch (name) {
      case "correct":
        playTone(523.25, "sine", 0.12, 0);
        playTone(659.25, "sine", 0.18, 0.08);
        break;
      case "wrong":
        playTone(220, "sawtooth", 0.15, 0);
        playTone(180, "sawtooth", 0.2, 0.08);
        break;
      case "hint":
        playTone(587.33, "triangle", 0.15, 0);
        playTone(880.0, "triangle", 0.25, 0.1);
        break;
      case "win":
        playTone(440, "sine", 0.12, 0);
        playTone(554.37, "sine", 0.12, 0.1);
        playTone(659.25, "sine", 0.15, 0.2);
        playTone(880, "sine", 0.35, 0.3);
        break;
      case "lose":
        playTone(293.66, "triangle", 0.2, 0);
        playTone(261.63, "triangle", 0.25, 0.18);
        playTone(220.0, "triangle", 0.4, 0.36);
        break;
    }
  } catch (e) {
    // Audio is optional
  }
}

// ==============================================================================
// 4. DOM ELEMENTS
// ==============================================================================

const wordDisplayEl = document.getElementById("wordDisplay");
const keyboardEl = document.getElementById("keyboard");
const hintTextEl = document.getElementById("hintText");
const hintContentEl = document.getElementById("hintContent");
const revealHintBtn = document.getElementById("revealHintBtn");
const statusBannerEl = document.getElementById("statusBanner");
const statusTextEl = document.getElementById("statusText");
const statusIconEl = document.getElementById("statusIcon");
const mistakesCounterEl = document.getElementById("mistakesCounter");
const livesIndicatorEl = document.getElementById("livesIndicator");
const solveInputEl = document.getElementById("solveInput");
const solveBtn = document.getElementById("solveBtn");

// Stats Ribbon Elements
const statGamesEl = document.getElementById("statGames");
const statWinsEl = document.getElementById("statWins");
const statLossesEl = document.getElementById("statLosses");
const statStreakEl = document.getElementById("statStreak");
const statWinRateEl = document.getElementById("statWinRate");

// History Elements
const historyChipsEl = document.getElementById("historyChips");
const historyScrollTrackEl = document.getElementById("historyScrollTrack");
const historyCountBadgeEl = document.getElementById("historyCountBadge");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");

// Modal Elements
const endGameModal = document.getElementById("endGameModal");
const modalGraphic = document.getElementById("modalGraphic");
const modalTitle = document.getElementById("modalTitle");
const modalSubtitle = document.getElementById("modalSubtitle");
const modalSecretWord = document.getElementById("modalSecretWord");
const modalSecretHint = document.getElementById("modalSecretHint");
const modalMistakes = document.getElementById("modalMistakes");
const modalStreak = document.getElementById("modalStreak");
const modalWinRate = document.getElementById("modalWinRate");
const modalPlayAgainBtn = document.getElementById("modalPlayAgainBtn");
const modalCloseBtn = document.getElementById("modalCloseBtn");

function updateStatsUI() {
  statGamesEl.textContent = stats.games;
  statWinsEl.textContent = stats.wins;
  statLossesEl.textContent = stats.losses;
  statStreakEl.textContent = stats.streak;
  const rate = stats.games > 0 ? ((stats.wins / stats.games) * 100).toFixed(0) : 0;
  statWinRateEl.textContent = `${rate}%`;
}

function renderGuessHistory() {
  if (!historyChipsEl) return;
  if (guessHistory.length === 0) {
    historyChipsEl.innerHTML = '<span class="history-empty">No letters guessed yet</span>';
    return;
  }
  historyChipsEl.innerHTML = guessHistory
    .map(
      (item) => `
      <span class="guess-chip ${item.isCorrect ? "correct" : "wrong"}">
        ${item.letter} <span class="chip-icon">${item.isCorrect ? "✓" : "✗"}</span>
      </span>`
    )
    .join("");
}

function renderMatchHistory() {
  if (!historyScrollTrackEl) return;

  if (historyCountBadgeEl) {
    historyCountBadgeEl.textContent = `${matchHistory.length} Game${matchHistory.length === 1 ? "" : "s"}`;
  }

  if (matchHistory.length === 0) {
    historyScrollTrackEl.innerHTML = '<div class="history-empty-placeholder">No completed games yet. Finish a round to log your match history!</div>';
    return;
  }

  historyScrollTrackEl.innerHTML = matchHistory
    .map(
      (g) => `
    <div class="history-card-item ${g.isWin ? "win" : "loss"}">
      <div class="history-card-top">
        <span class="history-badge ${g.isWin ? "win" : "loss"}">${g.isWin ? "WON" : "LOST"}</span>
        <span class="history-card-cat">${g.category}</span>
      </div>
      <div class="history-card-word">${g.word}</div>
      <div class="history-card-footer">
        <span>${g.mistakes}/${g.maxMistakes} mistakes</span>
        <span>${g.timestamp}</span>
      </div>
    </div>`
    )
    .join("");
}

function updateLivesIndicator() {
  const remaining = MAX_MISTAKES - incorrectGuesses;
  let hearts = "";
  for (let i = 0; i < MAX_MISTAKES; i++) {
    hearts += i < remaining ? "❤️" : "🖤";
  }
  livesIndicatorEl.innerHTML = hearts;
  mistakesCounterEl.innerHTML = `Mistakes: <strong>${incorrectGuesses} / ${MAX_MISTAKES}</strong>`;
}

function renderKeyboard() {
  keyboardEl.innerHTML = "";
  KEYBOARD_LAYOUT.forEach((row) => {
    const rowEl = document.createElement("div");
    rowEl.className = "keyboard-row";
    row.forEach((letter) => {
      const keyBtn = document.createElement("button");
      keyBtn.className = "key-btn";
      keyBtn.textContent = letter;
      keyBtn.id = `key-${letter}`;
      keyBtn.type = "button";
      keyBtn.addEventListener("click", (e) => {
        e.preventDefault();
        handleGuess(letter);
      });
      rowEl.appendChild(keyBtn);
    });
    keyboardEl.appendChild(rowEl);
  });
}

function updateKeyboardKey(letter, isCorrect) {
  const keyBtn = document.getElementById(`key-${letter.toUpperCase()}`);
  if (keyBtn) {
    keyBtn.disabled = true;
    keyBtn.classList.add(isCorrect ? "correct" : "wrong");
  }
}

function renderWordTiles(revealAll = false) {
  wordDisplayEl.innerHTML = "";
  for (const char of secretWord) {
    const tile = document.createElement("div");
    if (char === " ") {
      tile.className = "letter-tile space";
    } else {
      const isGuessed = guessedLetters.has(char.toLowerCase());
      tile.className = `letter-tile ${isGuessed || revealAll ? "revealed" : ""}`;
      tile.textContent = isGuessed || revealAll ? char.toUpperCase() : "";
    }
    wordDisplayEl.appendChild(tile);
  }
}

function updateHangmanSvg() {
  HANGMAN_PARTS.forEach((partId, index) => {
    const el = document.getElementById(partId);
    if (el) {
      if (index < incorrectGuesses) {
        el.classList.add("visible");
      } else {
        el.classList.remove("visible");
      }
    }
  });
}

function setStatus(text, type = "info", icon = "⚡") {
  statusTextEl.textContent = text;
  statusIconEl.textContent = icon;
  statusBannerEl.className = `status-banner ${type}`;
}

// ==============================================================================
// 5. GAME ENGINE LOGIC
// ==============================================================================

function startNewGame() {
  isGameOver = false;
  guessedLetters.clear();
  guessHistory = [];
  incorrectGuesses = 0;
  hintRevealed = false;

  // Choose secret word
  let wordPool = [];
  if (currentCategory === "Random") {
    Object.values(CATEGORIES).forEach((cat) => wordPool.push(...cat));
  } else {
    wordPool = CATEGORIES[currentCategory] || CATEGORIES.Programming;
  }

  const selected = wordPool[Math.floor(Math.random() * wordPool.length)];
  secretWord = selected.word.toLowerCase();
  currentHint = selected.hint;

  // Reset UI elements
  renderWordTiles();
  renderKeyboard();
  renderGuessHistory();
  updateHangmanSvg();
  updateLivesIndicator();
  updateStatsUI();

  // Reset Hint bar
  hintContentEl.classList.remove("revealed");
  hintTextEl.textContent = "Need a clue? Click Reveal Hint!";
  revealHintBtn.disabled = false;
  revealHintBtn.textContent = "Reveal Hint";

  // Reset Solve Input
  solveInputEl.value = "";

  // Hide Modal
  endGameModal.classList.remove("active");

  setStatus(`Category: ${currentCategory}. Pick a letter or use physical keyboard!`, "info", "🎮");
}

function handleGuess(rawLetter) {
  // If user tries to guess after game over, automatically start a fresh game!
  if (isGameOver) {
    startNewGame();
  }

  const letter = rawLetter.toLowerCase();

  if (guessedLetters.has(letter)) {
    setStatus(`You already tried '${letter.toUpperCase()}'.`, "warning", "⚠️");
    return;
  }

  guessedLetters.add(letter);
  const isCorrect = secretWord.includes(letter);
  guessHistory.push({ letter: letter.toUpperCase(), isCorrect });
  renderGuessHistory();

  if (isCorrect) {
    playSound("correct");
    setStatus(`Good guess! '${letter.toUpperCase()}' is in the word!`, "success", "✅");
    updateKeyboardKey(letter, true);
    renderWordTiles();
    checkWinCondition();
  } else {
    incorrectGuesses++;
    playSound("wrong");
    setStatus(`That letter isn't in the word: '${letter.toUpperCase()}'.`, "danger", "❌");
    updateKeyboardKey(letter, false);
    updateHangmanSvg();
    updateLivesIndicator();
    checkLossCondition();
  }
}

function handleFullWordSolve() {
  if (isGameOver) {
    startNewGame();
    return;
  }

  const guess = solveInputEl.value.trim().toLowerCase();
  if (!guess) return;

  if (guess === secretWord) {
    for (const char of secretWord) guessedLetters.add(char);
    guessHistory.push({ letter: guess.toUpperCase(), isCorrect: true });
    renderGuessHistory();
    renderWordTiles();
    triggerEndGame(true);
  } else {
    incorrectGuesses++;
    guessHistory.push({ letter: guess.toUpperCase(), isCorrect: false });
    renderGuessHistory();
    playSound("wrong");
    setStatus(`'${guess.toUpperCase()}' is not correct. That letter isn't in the word.`, "danger", "❌");
    updateHangmanSvg();
    updateLivesIndicator();
    solveInputEl.value = "";
    checkLossCondition();
  }
}

function checkWinCondition() {
  const isWon = [...secretWord].every(
    (char) => char === " " || guessedLetters.has(char)
  );
  if (isWon) {
    triggerEndGame(true);
  }
}

function checkLossCondition() {
  if (incorrectGuesses >= MAX_MISTAKES) {
    triggerEndGame(false);
  }
}

function triggerEndGame(isWin) {
  isGameOver = true;

  stats.games++;
  if (isWin) {
    stats.wins++;
    stats.streak++;
    if (stats.streak > stats.bestStreak) stats.bestStreak = stats.streak;
    playSound("win");
    startConfetti();
    setStatus(`You got it! The word was: ${secretWord.toUpperCase()}`, "success", "🎉");
  } else {
    stats.losses++;
    stats.streak = 0;
    playSound("lose");
    setStatus(`Out of guesses! The word was: ${secretWord.toUpperCase()}`, "danger", "💀");
    renderWordTiles(true);
  }

  saveStats();
  updateStatsUI();

  // Record in Match History
  const record = {
    word: secretWord.toUpperCase(),
    isWin: isWin,
    category: currentCategory,
    mistakes: incorrectGuesses,
    maxMistakes: MAX_MISTAKES,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
  matchHistory.unshift(record);
  if (matchHistory.length > 25) matchHistory.pop();
  try {
    localStorage.setItem("hangman_match_history", JSON.stringify(matchHistory));
  } catch (e) {}
  renderMatchHistory();

  // Populate and show Modal after short delay
  setTimeout(() => {
    modalGraphic.textContent = isWin ? "🎉" : "💀";
    modalTitle.textContent = isWin ? "Victory!" : "Game Over!";
    modalSubtitle.textContent = isWin
      ? "You successfully saved the hangman!"
      : "Out of guesses! Better luck next round!";
    modalSecretWord.textContent = secretWord.toUpperCase();
    modalSecretHint.textContent = currentHint;
    modalMistakes.textContent = `${incorrectGuesses} / ${MAX_MISTAKES}`;
    modalStreak.textContent = stats.streak;
    const rate = ((stats.wins / stats.games) * 100).toFixed(0);
    modalWinRate.textContent = `${rate}%`;
    endGameModal.classList.add("active");
  }, 600);
}

// ==============================================================================
// 6. CONFETTI EFFECT
// ==============================================================================

const confettiCanvas = document.getElementById("confettiCanvas");
const ctx = confettiCanvas.getContext("2d");
let confettiParticles = [];
let confettiAnimationId = null;

function resizeCanvas() {
  confettiCanvas.width = window.innerWidth;
  confettiCanvas.height = window.innerHeight;
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

function startConfetti() {
  confettiParticles = [];
  const colors = ["#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#06b6d4"];
  for (let i = 0; i < 90; i++) {
    confettiParticles.push({
      x: Math.random() * confettiCanvas.width,
      y: Math.random() * -confettiCanvas.height,
      size: Math.random() * 7 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      speedY: Math.random() * 3 + 2,
      speedX: Math.random() * 3 - 1.5,
      rotation: Math.random() * 360,
      rotSpeed: Math.random() * 4 - 2
    });
  }

  if (confettiAnimationId) cancelAnimationFrame(confettiAnimationId);
  animateConfetti();
  setTimeout(() => cancelAnimationFrame(confettiAnimationId), 3000);
}

function animateConfetti() {
  ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
  confettiParticles.forEach((p) => {
    p.y += p.speedY;
    p.x += p.speedX;
    p.rotation += p.rotSpeed;

    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate((p.rotation * Math.PI) / 180);
    ctx.fillStyle = p.color;
    ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
    ctx.restore();
  });
  confettiAnimationId = requestAnimationFrame(animateConfetti);
}

// ==============================================================================
// 7. EVENT LISTENERS
// ==============================================================================

// Physical Keyboard Listener
window.addEventListener("keydown", (e) => {
  // Escape closes modal
  if (e.key === "Escape" && endGameModal.classList.contains("active")) {
    endGameModal.classList.remove("active");
    if (isGameOver) startNewGame();
    return;
  }

  // If typing in solve input
  if (document.activeElement === solveInputEl) {
    if (e.key === "Enter") {
      e.preventDefault();
      handleFullWordSolve();
    }
    return;
  }

  // If game is over, pressing Enter or Space restarts
  if (isGameOver) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      startNewGame();
    }
    return;
  }

  // Letter input
  if (/^[a-zA-Z]$/.test(e.key)) {
    e.preventDefault();
    handleGuess(e.key.toUpperCase());
  }
});

// Category pills click
document.querySelectorAll(".cat-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".cat-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentCategory = btn.dataset.category;
    startNewGame();
  });
});

// Hint button
revealHintBtn.addEventListener("click", () => {
  if (hintRevealed || isGameOver) return;
  hintRevealed = true;
  playSound("hint");
  hintContentEl.classList.add("revealed");
  hintTextEl.textContent = currentHint;
  revealHintBtn.disabled = true;
  revealHintBtn.textContent = "Hint Used";
  setStatus(`Clue revealed: ${currentHint}`, "info", "💡");
});

// Solve Word
solveBtn.addEventListener("click", handleFullWordSolve);
solveInputEl.addEventListener("keypress", (e) => {
  if (e.key === "Enter") handleFullWordSolve();
});

// Modal Actions
modalPlayAgainBtn.addEventListener("click", () => {
  endGameModal.classList.remove("active");
  startNewGame();
});

modalCloseBtn.addEventListener("click", () => {
  endGameModal.classList.remove("active");
  if (isGameOver) startNewGame();
});

// New Game Buttons (Top & Bottom)
document.getElementById("newGameBtn").addEventListener("click", startNewGame);
document.getElementById("newGameTopBtn").addEventListener("click", startNewGame);

// View Statistics Modal Button (Top Right 📊)
document.getElementById("statsModalBtn").addEventListener("click", () => {
  modalGraphic.textContent = "📊";
  modalTitle.textContent = "Game Statistics";
  modalSubtitle.textContent = "Current session summary";
  modalSecretWord.textContent = secretWord.toUpperCase();
  modalSecretHint.textContent = currentHint;
  modalMistakes.textContent = `${incorrectGuesses} / ${MAX_MISTAKES}`;
  modalStreak.textContent = stats.streak;
  const rate = stats.games > 0 ? ((stats.wins / stats.games) * 100).toFixed(0) : 0;
  modalWinRate.textContent = `${rate}%`;
  endGameModal.classList.add("active");
});

// Reset Stats Button
document.getElementById("resetStatsBtn").addEventListener("click", () => {
  if (confirm("Reset all game statistics and match history to zero?")) {
    stats = { games: 0, wins: 0, losses: 0, streak: 0, bestStreak: 0 };
    matchHistory = [];
    saveStats();
    try {
      localStorage.removeItem("hangman_match_history");
    } catch (e) {}
    updateStatsUI();
    renderMatchHistory();
  }
});

// Clear Match History Button
if (clearHistoryBtn) {
  clearHistoryBtn.addEventListener("click", () => {
    if (confirm("Clear your match history?")) {
      matchHistory = [];
      try {
        localStorage.removeItem("hangman_match_history");
      } catch (e) {}
      renderMatchHistory();
    }
  });
}

// Sound Toggle
const soundToggleBtn = document.getElementById("soundToggleBtn");
soundToggleBtn.addEventListener("click", () => {
  soundEnabled = !soundEnabled;
  soundToggleBtn.textContent = soundEnabled ? "🔊" : "🔇";
});

// Theme Toggle
const themeToggleBtn = document.getElementById("themeToggleBtn");
themeToggleBtn.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  themeToggleBtn.textContent = next === "light" ? "☀️" : "🌙";
});

// Launch First Game on load
startNewGame();
renderMatchHistory();
