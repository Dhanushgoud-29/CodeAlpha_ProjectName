# Hangman Game

A beginner-friendly, text-based Hangman game written in Python. The computer
randomly selects one of five built-in words, and the player guesses it one
letter at a time in the console.

## CodeAlpha Internship Task

This project was created for **CodeAlpha Python Programming Internship —
Task 1: Hangman Game**. It follows the task requirements: five predefined
words, one-letter guesses, and a limit of six incorrect guesses.

## Features

- **Dynamic Visual Dashboard**: Real-time ASCII gallows art advancing through 7 distinct visual stages (0 to 6 mistakes).
- **Live Health Meter Bar**: Visual health indicator displaying remaining lives (e.g. `[■ ■ ■ ■ □ □]`).
- **Interactive Alphabet Tracker**: Two-row A–Z alphabet tracker clearly displaying available letters vs. already attempted letters (`[A]`).
- **Multi-Category Word Bank with Hints**: Includes the core CodeAlpha 5-word list (`Programming`), plus bonus categories (`Animals`, `Countries`, `Science`, and `Random Mix`), each featuring contextual hints.
- **Smart Input & Solving**: Supports standard single-letter guesses, whole-word solution attempts (e.g. `python`), and hint requests (`?`).
- **Session Scoreboard**: Tracks total games played, victories, defeats, current win streak, best win streak, and win rate %.
- **Safe & Graceful**: Fully handles repeated guesses, invalid characters, and clean exits (`Ctrl+C` / EOF) without crashing.
- **Pure Python**: 100% standard library (`random`, `os`, `sys`, `string`) with zero external pip dependencies.

## Technologies

- Python 3
- Python standard library (`random`, `os`, `sys`, `string`)
- Visual Studio Code / Terminal

No external packages, graphics, audio, web services, or databases are used.
`requirements.txt` is included for project completeness; there is nothing to
install with pip.

## Project structure

```text
CodeAlpha_HangmanGame/
├── main.py                  # Pro Developer OOP Game Engine & CLI
├── tests/
│   └── test_hangman.py      # Automated Unit Test Suite (13 tests)
├── index.html               # Web Edition: Modern Interactive Game
├── style.css                # Web Edition: Responsive Glassmorphism Styling
├── app.js                   # Web Edition: Game Engine, Audio, Confetti
├── README.md                # Documentation & Internship Guide
├── requirements.txt         # Zero dependencies (Standard Library)
├── .gitignore
└── screenshots/
    └── .gitkeep
```

The `.gitkeep` file lets Git include the otherwise-empty screenshots folder.
Save any screenshots you take in that folder.

## Install Python

1. Download Python 3 from [python.org](https://www.python.org/downloads/).
2. On Windows, run the installer and select **Add Python to PATH**.
3. Open a terminal and check the installation:

   ```powershell
   py --version
   ```

   If `py` is not available, try `python --version`.

## Create and run the project in VS Code

1. Create a folder named `CodeAlpha_HangmanGame`.
2. In VS Code, choose **File > Open Folder...** and open that folder.
3. Create `main.py`, `README.md`, `requirements.txt`, and `.gitignore`.
   Create a `screenshots` subfolder as well.
4. Paste the corresponding project contents into each file. The `.gitkeep`
   file in `screenshots` is optional when creating the project manually.
5. In VS Code, open **Terminal > New Terminal**.
6. Confirm the terminal is in the project folder, then run:

   ```powershell
   py main.py
   ```

   You can use `python main.py` if that is the Python command on your system.
7. Type one letter and press Enter to play. No dependencies need to be
   installed.

## Web Edition (Play in Browser)

In addition to the console version, this repository includes a complete client-side Web Edition:

1. Double-click `index.html` or open it in your browser (Chrome, Edge, Firefox).
2. Alternatively, start a local preview server from the terminal:
   ```powershell
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser.
3. **GitHub Pages Deployment**: You can host it for free on GitHub Pages by going to your GitHub repository's **Settings > Pages** and selecting the `main` branch.

## How to play (Console Edition)

1. The game picks a word and shows each letter as `_`.
2. Enter one letter and press Enter.
3. Correct letters appear in the word. Incorrect guesses use one of the six
   allowed mistakes.
4. Previously guessed letters and remaining mistakes are shown each turn.
5. Guess every letter before making six incorrect guesses to win.
6. At the end of the round, enter `y` to play again or `n` to quit.

Uppercase input is converted to lowercase. Inputs that are not exactly one
alphabetic character are rejected. Repeated guesses are reported without
using an attempt.

## Sample output

```text
============================================================================
                🎮  H A N G M A N   D A S H B O A R D  🎮
============================================================================
 [STATS] Games: 1 | Wins: 1 | Losses: 0 | Streak: 1 (Best: 1) | Win Rate: 100.0%
----------------------------------------------------------------------------
     +---+        │  Category : Programming (CodeAlpha Core)
     |   |        │  Word     : p y t h _ n
     O   |        │  
    /|   |        │  Health   : [■ ■ ■ ■ □ □]  (4/6 lives left)
         |        │  Tried    : p, y, t, h, n, e, a
         |        │  Hint     : 💡 A popular interpreted language named after Monty Python
  =========       │  Wrong guesses left: 4/6
----------------------------------------------------------------------------
 Alphabet Tracker (tried letters in brackets):
  [A]  B   C   D  [E]  F   G  [H]  I   J   K   L   M 
  [N] [O] [P]  Q   R   S  [T]  U   V   W   X  [Y]  Z 
----------------------------------------------------------------------------
 Status: Good guess!
============================================================================
Your guess: 
```

## Testing checklist

Run `py main.py` and exercise these cases. Since the word is random, use the
displayed word and adjust your guesses to match each case.

| Case | What to check |
| --- | --- |
| Correct letter | A letter in the word is revealed; remaining attempts do not change. |
| Incorrect letter | A letter not in the word is recorded; attempts decrease by one. |
| Repeated letter | Enter a previously guessed letter; it is rejected and attempts do not change. |
| Invalid input | Try `7`, `ab`, or an empty line; each is rejected without using an attempt. |
| Win | Guess all distinct letters shown in the word; the game prints a win message. |
| Loss | Guess six different letters absent from the word; the game prints the word. |
| Play again | Enter `y` after a round to begin another; enter `n` to exit. |

Important expected messages:

```text
Good guess!
That letter isn't in the word.
You already tried that letter.
Please enter just one letter.
You got it! The word was python.
Out of guesses! The word was python.
Thanks for playing!
```

The word in the final two examples is illustrative; it depends on the random
selection in the actual game.

## Beginner explanation

### `main.py`

This is the game's Python source file. It imports standard modules (`random`, `os`, `sys`, `string`), defines categories and the maximum allowed mistakes (6), then implements clean, modular functions:

- `clear_screen()` cleans the console between turns for an interactive terminal feel, falling back safely if running in a non-interactive pipe.
- `display_word(secret_word, guessed_letters)` builds the word string, showing guessed characters and masking remaining characters with underscores.
- `format_health_bar(incorrect_guesses, max_incorrect)` renders the visual health meter bar (`[■ ■ ■ ■ □ □]`).
- `format_alphabet_tracker(guessed_letters)` builds a 2-row A-Z tracker with tried letters bracketed (`[A]`), giving the player instant visibility into unused letters.
- `show_dashboard(...)` assembles and displays the side-by-side ASCII gallows, current secret word, health bar, session scoreboard, alphabet tracker, and real-time status banner.
- `select_category()` lets the player choose a category (Programming, Animals, Countries, Science, or Random Mix).
- `get_player_guess(guessed_letters)` prompts the player and validates their input: accepts single-letter guesses, whole-word guesses, and hint requests (`?`).
- `play_game(stats)` runs one full round, updates the session statistics, and displays victory or defeat screens.
- `ask_play_again()` handles the round replay prompt.
- `show_session_summary(stats)` prints the final player report card when quitting.
- `main()` manages session statistics across rounds and guards against sudden exits (`KeyboardInterrupt`, `EOFError`).

### Other files

- `README.md` (this file) explains setup, play, testing, and publishing.
- `requirements.txt` documents that the project has no third-party
  dependencies.
- `.gitignore` tells Git not to track Python cache files and local editor or
  environment files.
- `screenshots/.gitkeep` keeps the empty screenshots folder in the repository.

## Publish the project on GitHub

First, sign in to GitHub and create a **public** repository named
`CodeAlpha_HangmanGame`. Do not initialize it with a README, license, or
`.gitignore`, because those files already exist locally.

Open a terminal in the project folder and run these commands. Replace
`YOUR_USERNAME` with your GitHub username:

```powershell
git init
git add .
git commit -m "Create CodeAlpha Hangman game"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/CodeAlpha_HangmanGame.git
git push -u origin main
```

What each command does:

1. `git init` starts version control in this folder.
2. `git add .` stages the project files for the next commit.
3. `git commit ...` saves the staged files as a named checkpoint.
4. `git branch -M main` names the current branch `main`.
5. `git remote add origin ...` connects the local project to your GitHub
   repository. Replace the placeholder URL with your repository's URL.
6. `git push -u origin main` uploads the branch and sets its upstream for
   future pushes.

Git does not create the hosted GitHub repository itself; create it on GitHub
first as described above. For later updates, use `git add .`, `git commit -m
"Describe your update"`, and `git push`.

## Optional: Building a Windows Executable

If you ever wish to package the console game into a standalone `.exe` without needing Python:

```powershell
pyinstaller --onefile --name "HangmanPro" --clean main.py
```

This is purely optional; the standard Python application `python main.py` is the official way to run the game for the internship.

## Running the Automated Unit Test Suite

The project includes an enterprise-grade test suite covering game engine state transitions, word display formatting, input validation, and score persistence:

```powershell
python -m unittest discover tests
```

Expected output:
```text
.............
----------------------------------------------------------------------
Ran 13 tests in 0.005s

OK
```

## CLI Arguments (Pro Developer Features)

You can launch the game with command-line flags:

```powershell
# Set difficulty: easy (8 lives), medium (6 lives), or hard (4 lives)
python main.py --difficulty hard

# Pre-select category: 1=Programming, 2=Animals, 3=Countries, 4=Science, 5=Random
python main.py --category 1

# View your persistent career stats & high scores
python main.py --stats

# Reset career statistics
python main.py --reset-stats
```

## Project demonstration script

> Hi, I'm **[Your Name]**, and this is my Hangman Game project for the
> CodeAlpha Python Programming Internship. It's a console application built
> with Python's standard library. The game randomly chooses from five words,
> reveals correct letter guesses, and allows up to six incorrect guesses.
> It also validates input, prevents repeated guesses from using an attempt,
> and lets the player start another round. I created it to practice
> functions, loops, lists, conditionals, input handling, and the `random`
> module. The source code and instructions are available in my GitHub
> repository: **[GitHub profile or repository link]**.

## Interview questions and answers

**1. How does the game choose its word?**  
It calls `random.choice(WORDS)`, which returns one randomly selected item
from the predefined list.

**2. How are hidden letters displayed?**  
`display_word()` checks every character against the list of guessed letters.
It returns the character when it has been guessed and `_` otherwise.

**3. How does the game track incorrect guesses?**  
The `incorrect_guesses` variable starts at zero and increases only when a
new, valid guess is not in the word. The round ends at six.

**4. Why are repeated guesses checked before they are processed?**  
So the player gets feedback without accidentally spending an incorrect
attempt or counting a letter twice.

**5. How does the game decide that the player won?**  
It uses `all()` to check that each character in the secret word appears in
the guessed-letter list.

**6. Which Python concepts does the project demonstrate?**  
Variables, strings, lists, functions, loops, conditionals, user input, and
the standard-library `random` module.

## Author

- **Name:** [Your Name]
- **GitHub:** [Your GitHub profile URL]
