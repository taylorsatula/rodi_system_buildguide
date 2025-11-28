let ws = null;
let roomCode = null;
let hostId = null;
let gameState = null;

// Initialize on page load
window.addEventListener('DOMContentLoaded', async () => {
    await createRoom();
    setupEventListeners();
});

async function createRoom() {
    try {
        const response = await fetch('/api/create-room', {
            method: 'POST',
        });
        const data = await response.json();
        roomCode = data.room_code;
        hostId = data.host_id;

        document.getElementById('room-code').textContent = roomCode;
        const joinUrl = `${window.location.origin}/play`;
        document.getElementById('join-url').textContent = joinUrl;

        // Connect to WebSocket
        connectWebSocket();
    } catch (error) {
        console.error('Error creating room:', error);
    }
}

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${roomCode}`;

    ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'state_update') {
            gameState = message.state;
            updateUI();
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket closed');
    };
}

function setupEventListeners() {
    document.getElementById('start-game-btn').addEventListener('click', () => {
        hostAction('start_game');
    });

    document.getElementById('start-answering-btn').addEventListener('click', () => {
        hostAction('start_answering');
    });

    document.getElementById('judge-answers-btn').addEventListener('click', () => {
        hostAction('judge_answers');
    });

    document.getElementById('next-question-btn').addEventListener('click', () => {
        hostAction('next_question');
    });

    document.getElementById('new-game-btn').addEventListener('click', () => {
        window.location.reload();
    });
}

async function hostAction(action) {
    try {
        await fetch('/api/host-action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_code: roomCode,
                action: action,
            }),
        });
    } catch (error) {
        console.error('Error performing host action:', error);
    }
}

function updateUI() {
    if (!gameState) return;

    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });

    // Show appropriate screen based on game phase
    switch (gameState.phase) {
        case 'lobby':
            showLobbyScreen();
            break;
        case 'question':
            showQuestionScreen();
            break;
        case 'answering':
            showAnsweringScreen();
            break;
        case 'judging':
            showJudgingScreen();
            break;
        case 'results':
            showResultsScreen();
            break;
        case 'final_scores':
            showFinalScoresScreen();
            break;
    }
}

function showLobbyScreen() {
    document.getElementById('lobby-screen').classList.remove('hidden');

    const lobbyPlayers = document.getElementById('lobby-players');
    lobbyPlayers.innerHTML = '';

    const playerCount = Object.keys(gameState.players).length;

    if (playerCount === 0) {
        lobbyPlayers.innerHTML = '<p style="opacity: 0.7; font-size: 1.5rem;">Waiting for players to join...</p>';
    } else {
        Object.values(gameState.players).forEach(player => {
            const playerCard = document.createElement('div');
            playerCard.className = 'player-card';
            playerCard.textContent = player.name;
            lobbyPlayers.appendChild(playerCard);
        });
    }
}

function showQuestionScreen() {
    document.getElementById('question-screen').classList.remove('hidden');

    const currentQuestion = gameState.questions[gameState.current_question_index];

    document.getElementById('question-number').textContent =
        `Question ${gameState.current_question_index + 1} of ${gameState.questions.length}`;

    document.getElementById('question-category').textContent =
        currentQuestion.category || 'General';

    document.getElementById('question-text').textContent = currentQuestion.text;
}

function showAnsweringScreen() {
    document.getElementById('answering-screen').classList.remove('hidden');

    const currentQuestion = gameState.questions[gameState.current_question_index];

    document.getElementById('answering-question-number').textContent =
        `Question ${gameState.current_question_index + 1} of ${gameState.questions.length}`;

    document.getElementById('answering-question-text').textContent = currentQuestion.text;

    const statusContainer = document.getElementById('answering-status');
    statusContainer.innerHTML = '';

    Object.values(gameState.players).forEach(player => {
        const statusCard = document.createElement('div');
        statusCard.className = player.answer_submitted
            ? 'player-status submitted'
            : 'player-status waiting';

        statusCard.innerHTML = `
            <div style="font-weight: bold;">${player.name}</div>
            <div style="margin-top: 0.5rem; opacity: 0.8;">
                ${player.answer_submitted ? '✓ Answered' : '⏱ Thinking...'}
            </div>
        `;

        statusContainer.appendChild(statusCard);
    });
}

function showJudgingScreen() {
    document.getElementById('judging-screen').classList.remove('hidden');
}

function showResultsScreen() {
    document.getElementById('results-screen').classList.remove('hidden');

    const currentQuestion = gameState.questions[gameState.current_question_index];
    document.getElementById('correct-answer-text').textContent = currentQuestion.correct_answer;

    const judgementsContainer = document.getElementById('judgements');
    judgementsContainer.innerHTML = '';

    // Sort judgements by points (correct first, then by player name)
    const sortedJudgements = [...gameState.current_judgements].sort((a, b) => {
        if (a.is_correct !== b.is_correct) {
            return b.is_correct ? 1 : -1;
        }
        return a.player_name.localeCompare(b.player_name);
    });

    sortedJudgements.forEach(judgement => {
        const card = document.createElement('div');
        card.className = `judgement-card ${judgement.is_correct ? 'correct' : 'incorrect'}`;

        card.innerHTML = `
            <div class="judgement-header">
                <span class="player-name">${judgement.player_name}</span>
                <span class="points">${judgement.is_correct ? '✓' : '✗'} ${judgement.points_awarded} pts</span>
            </div>
            <div class="player-answer">"${judgement.answer}"</div>
            <div class="reasoning">${judgement.reasoning}</div>
        `;

        judgementsContainer.appendChild(card);
    });

    // Update button text for last question
    const nextBtn = document.getElementById('next-question-btn');
    if (gameState.current_question_index >= gameState.questions.length - 1) {
        nextBtn.textContent = 'Show Final Scores';
    } else {
        nextBtn.textContent = 'Next Question';
    }
}

function showFinalScoresScreen() {
    document.getElementById('final-screen').classList.remove('hidden');

    const scoresContainer = document.getElementById('final-scores');
    scoresContainer.innerHTML = '';

    // Sort players by score
    const sortedPlayers = Object.values(gameState.players).sort((a, b) => b.score - a.score);

    sortedPlayers.forEach((player, index) => {
        const card = document.createElement('div');
        card.className = 'score-card';

        let medal = '';
        if (index === 0) medal = '🥇';
        else if (index === 1) medal = '🥈';
        else if (index === 2) medal = '🥉';

        card.innerHTML = `
            <span class="rank">${medal || `#${index + 1}`}</span>
            <span class="name">${player.name}</span>
            <span class="score">${player.score}</span>
        `;

        scoresContainer.appendChild(card);
    });
}
