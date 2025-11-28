let ws = null;
let roomCode = null;
let playerId = null;
let playerName = null;
let gameState = null;

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();

    // Check if we have stored player info (for page refresh)
    const storedPlayerId = sessionStorage.getItem('playerId');
    const storedRoomCode = sessionStorage.getItem('roomCode');
    const storedPlayerName = sessionStorage.getItem('playerName');

    if (storedPlayerId && storedRoomCode && storedPlayerName) {
        playerId = storedPlayerId;
        roomCode = storedRoomCode;
        playerName = storedPlayerName;
        connectWebSocket();
        showWaitingScreen();
    }
});

function setupEventListeners() {
    document.getElementById('join-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await joinRoom();
    });

    document.getElementById('answer-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitAnswer();
    });

    // Auto-uppercase room code
    const roomCodeInput = document.getElementById('room-code-input');
    roomCodeInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.toUpperCase();
    });
}

async function joinRoom() {
    const roomCodeInput = document.getElementById('room-code-input').value.trim().toUpperCase();
    const playerNameInput = document.getElementById('player-name-input').value.trim();

    if (!roomCodeInput || !playerNameInput) {
        alert('Please enter both room code and your name');
        return;
    }

    try {
        const response = await fetch('/api/join-room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_code: roomCodeInput,
                player_name: playerNameInput,
            }),
        });

        if (!response.ok) {
            throw new Error('Could not join room');
        }

        const data = await response.json();
        playerId = data.player_id;
        roomCode = data.room_code;
        playerName = playerNameInput;

        // Store in session storage
        sessionStorage.setItem('playerId', playerId);
        sessionStorage.setItem('roomCode', roomCode);
        sessionStorage.setItem('playerName', playerName);

        // Connect to WebSocket
        connectWebSocket();

        // Show waiting screen
        showWaitingScreen();
    } catch (error) {
        console.error('Error joining room:', error);
        alert('Could not join room. Please check the room code and try again.');
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

function showWaitingScreen() {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });
    document.getElementById('waiting-screen').classList.remove('hidden');
    document.getElementById('player-name-display').textContent = playerName;
}

async function submitAnswer() {
    const answer = document.getElementById('answer-input').value.trim();

    if (!answer) {
        return;
    }

    try {
        await fetch('/api/submit-answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_code: roomCode,
                player_id: playerId,
                answer: answer,
            }),
        });

        // Clear input
        document.getElementById('answer-input').value = '';
    } catch (error) {
        console.error('Error submitting answer:', error);
        alert('Could not submit answer. Please try again.');
    }
}

function updateUI() {
    if (!gameState || !playerId) return;

    const player = gameState.players[playerId];
    if (!player) return;

    // Update score displays
    document.getElementById('score').textContent = player.score;
    document.getElementById('current-score').textContent = player.score;
    document.getElementById('final-score').textContent = player.score;

    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });

    // Show appropriate screen based on game phase and player state
    switch (gameState.phase) {
        case 'lobby':
            showWaitingScreen();
            break;
        case 'question':
            showQuestionDisplayScreen();
            break;
        case 'answering':
            if (player.answer_submitted) {
                showSubmittedScreen();
            } else {
                showAnswerScreen();
            }
            break;
        case 'judging':
            showSubmittedScreen();
            break;
        case 'results':
            showResultsScreen();
            break;
        case 'final_scores':
            showFinalScoresScreen();
            break;
    }
}

function showQuestionDisplayScreen() {
    document.getElementById('question-display-screen').classList.remove('hidden');
    const currentQuestion = gameState.questions[gameState.current_question_index];
    document.getElementById('question-preview').textContent = currentQuestion.text;
}

function showAnswerScreen() {
    document.getElementById('answer-screen').classList.remove('hidden');
    const currentQuestion = gameState.questions[gameState.current_question_index];
    document.getElementById('question-text-player').textContent = currentQuestion.text;

    // Focus on input
    setTimeout(() => {
        document.getElementById('answer-input').focus();
    }, 100);
}

function showSubmittedScreen() {
    document.getElementById('submitted-screen').classList.remove('hidden');
    const player = gameState.players[playerId];
    if (player.current_answer) {
        document.getElementById('submitted-answer-text').textContent = player.current_answer;
    }
}

function showResultsScreen() {
    document.getElementById('player-results-screen').classList.remove('hidden');

    const currentQuestion = gameState.questions[gameState.current_question_index];
    document.getElementById('correct-answer-player').textContent = currentQuestion.correct_answer;

    // Find this player's judgement
    const myJudgement = gameState.current_judgements.find(j => j.player_id === playerId);

    if (myJudgement) {
        const resultStatus = document.getElementById('result-status');
        if (myJudgement.is_correct) {
            resultStatus.textContent = `✓ Correct! +${myJudgement.points_awarded} pts`;
            resultStatus.className = 'result-status correct';
        } else {
            resultStatus.textContent = '✗ Incorrect';
            resultStatus.className = 'result-status incorrect';
        }

        const judgementBox = document.getElementById('player-judgement');
        judgementBox.innerHTML = `
            <div class="your-answer">Your answer: "${myJudgement.answer}"</div>
            <div class="reasoning">${myJudgement.reasoning}</div>
        `;
    }
}

function showFinalScoresScreen() {
    document.getElementById('player-final-screen').classList.remove('hidden');

    // Calculate placement
    const sortedPlayers = Object.values(gameState.players).sort((a, b) => b.score - a.score);
    const myIndex = sortedPlayers.findIndex(p => p.id === playerId);

    let placementText = '';
    if (myIndex === 0) {
        placementText = '🥇 1st Place!';
    } else if (myIndex === 1) {
        placementText = '🥈 2nd Place!';
    } else if (myIndex === 2) {
        placementText = '🥉 3rd Place!';
    } else {
        placementText = `#${myIndex + 1}`;
    }

    document.getElementById('final-placement').textContent = placementText;
}
