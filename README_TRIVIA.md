# 🎯 Trivia Night - LLM-Judged Multiplayer Trivia Game

A Jackbox-style trivia game where players use their phones to answer questions, and Claude AI judges the answers for semantic correctness.

## Features

- 🎮 **Jackbox-style gameplay** - Host display on main screen, players join with their phones
- 🤖 **AI-powered judging** - Claude Haiku 4.5 evaluates answers for semantic correctness
- ⚡ **Real-time updates** - WebSocket-based live game state synchronization
- 📱 **Mobile-friendly** - Responsive design for player devices
- 🎨 **Beautiful UI** - Modern gradient design with smooth animations

## Quick Start

### Prerequisites

- Python 3.8+
- Anthropic API key

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the trivia question database:
```bash
python init_trivia_db.py
```

This will create a SQLite database (`trivia.db`) with 120+ trivia questions across 11 categories.

3. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

4. Run the server:
```bash
python main.py
```

5. Open the game:
   - **Host Display**: http://localhost:8000
   - **Player Join**: http://localhost:8000/play

## How to Play

### For the Host

1. Open http://localhost:8000 on your main display (TV, projector, etc.)
2. A room code will be generated automatically
3. Share the room code with players
4. Wait for players to join
5. Click "Start Game" when ready
6. Control game flow with on-screen buttons:
   - "Start Answering" - Opens answer submission for players
   - "Judge Answers" - Sends answers to Claude for evaluation
   - "Next Question" - Moves to the next question

### For Players

1. Open http://localhost:8000/play on your phone
2. Enter the room code shown on the host display
3. Enter your name and join
4. Answer questions as they appear
5. See your results and score after each question

## How It Works

### LLM Judging

Instead of requiring exact string matches, Claude evaluates each answer for semantic correctness:

- ✅ **Lenient on**: spelling mistakes, different phrasing, additional context
- ❌ **Strict on**: wrong information, contradictions, random guesses

Each judgement includes a brief explanation of why the answer was marked correct or incorrect.

### Tech Stack

- **Backend**: FastAPI + WebSockets
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Database**: SQLite for question storage
- **LLM**: Claude 3.5 Haiku via Anthropic API
- **Real-time**: WebSocket-based state synchronization

## Project Structure

```
.
├── main.py              # FastAPI application and WebSocket server
├── models.py            # Pydantic models for game state
├── game_manager.py      # Game logic and room management
├── llm_judge.py         # Claude integration for answer judging
├── database.py          # SQLite database manager
├── init_trivia_db.py    # Database initialization script
├── trivia.db            # SQLite database (created by init script)
├── static/
│   ├── index.html       # Host display
│   ├── player.html      # Player interface
│   ├── css/
│   │   ├── host.css     # Host display styles
│   │   └── player.css   # Player interface styles
│   └── js/
│       ├── host.js      # Host display logic
│       └── player.js    # Player interface logic
└── requirements.txt     # Python dependencies
```

## Question Database

### Built-in Questions

The game includes 120+ trivia questions across 11 categories:
- **Geography** - Capitals, landmarks, and world knowledge
- **Science** - Physics, chemistry, biology, and astronomy
- **History** - World history, US history, and historical events
- **Literature** - Classic and modern literature
- **Music** - Instruments, composers, and music theory
- **Sports** - Rules, records, and sports knowledge
- **Movies** - Directors, actors, and film trivia
- **Art** - Painters, styles, and art history
- **Technology** - Computing, programming, and tech history
- **Food** - Cooking, ingredients, and cuisine
- **Mythology** - Greek, Roman, Norse, and Egyptian mythology

### Adding Your Own Questions

You can add questions to the database using Python:

```python
from database import trivia_db

trivia_db.add_question(
    text="Your question here?",
    correct_answer="The correct answer",
    category="Category Name",
    difficulty="easy",  # easy, medium, or hard
    points=100,
    source="Reference URL or source"
)
```

Or add multiple questions at once:

```python
questions = [
    {
        "text": "Question 1?",
        "correct_answer": "Answer 1",
        "category": "Category",
        "difficulty": "easy",
        "points": 100,
        "source": None
    },
    # ... more questions
]

trivia_db.add_questions_bulk(questions)
```

### Question Selection

The game automatically:
- Selects 8 random questions per game from the database
- Uses SQLite's `RANDOM()` function for efficient random selection
- Questions are unique per game session (no repeats within a single game)
- Falls back to hardcoded questions if the database is empty or unavailable

### Database Management

View database statistics:
```python
from database import trivia_db

# Get total question count
total = trivia_db.get_question_count()

# Get all categories
categories = trivia_db.get_categories()

# Get count by category
science_count = trivia_db.get_question_count(category="Science")
```

## Future Enhancements

- [x] SQLite database for question storage
- [x] Random question selection without repeats
- [x] Question categories and difficulty levels
- [ ] Import questions from Open Trivia Database API
- [ ] Category-specific games (e.g., "Science only")
- [ ] Difficulty-based scoring (harder questions = more points)
- [ ] Configurable game settings (rounds, time limits, timer per question)
- [ ] Answer timer with countdown on player devices
- [ ] Persistent scores and leaderboards
- [ ] Player statistics and achievements
- [ ] Custom question packs and themes
- [ ] Export/import question sets as JSON

## License

MIT
