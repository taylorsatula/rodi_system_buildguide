let ws = null;
let roomCode = null;
let playerId = null;
let playerName = null;
let gameState = null;
let isHost = false;
let timerInterval = null;

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();

    // Check for stored session
    const storedPlayerId = sessionStorage.getItem('playerId');
    const storedRoomCode = sessionStorage.getItem('roomCode');
    const storedPlayerName = sessionStorage.getItem('playerName');
    const storedIsHost = sessionStorage.getItem('isHost') === 'true';

    if (storedPlayerId && storedRoomCode && storedPlayerName) {
        playerId = storedPlayerId;
        roomCode = storedRoomCode;
        playerName = storedPlayerName;
        isHost = storedIsHost;
        connectWebSocket();
    }
});

function setupEventListeners() {
    document.getElementById('join-form').addEventListener('submit', handleJoin);
    document.getElementById('config-form').addEventListener('submit', handleConfigSubmit);
    document.getElementById('answer-form').addEventListener('submit', handleAnswerSubmit);
    document.getElementById('vote-yes').addEventListener('click', () => submitVote(true));
    document.getElementById('vote-no').addEventListener('click', () => submitVote(false));
    document.getElementById('new-game-btn').addEventListener('click', () => window.location.reload());

    // Auto-uppercase room code
    document.getElementById('room-code-input').addEventListener('input', (e) => {
        e.target.value = e.target.value.toUpperCase();
    });
}

async function handleJoin(e) {
    e.preventDefault();

    const roomCodeInput = document.getElementById('room-code-input').value.trim().toUpperCase();
    const playerNameInput = document.getElementById('player-name-input').value.trim();

    if (!roomCodeInput || !playerNameInput) {
        return;
    }

    try {
        const response = await fetch('/api/join-room', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_code: roomCodeInput,
                player_name: playerNameInput,
            }),
        });

        if (!response.ok) throw new Error('Could not join room');

        const data = await response.json();
        playerId = data.player_id;
        roomCode = data.room_code;
        playerName = playerNameInput;

        // Store in session
        sessionStorage.setItem('playerId', playerId);
        sessionStorage.setItem('roomCode', roomCode);
        sessionStorage.setItem('playerName', playerName);

        connectWebSocket();
    } catch (error) {
        console.error('Error joining room:', error);
        alert('Could not join room. Check the room code and try again.');
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

    ws.onerror = (error) => console.error('WebSocket error:', error);
    ws.onclose = () => console.log('WebSocket closed');
}

async function handleConfigSubmit(e) {
    e.preventDefault();

    const numQuestions = parseInt(document.getElementById('num-questions').value);
    const difficulty = document.getElementById('difficulty').value || null;
    const includeFinal = document.getElementById('final-question').checked;
    const answerTime = parseInt(document.getElementById('answer-time').value);

    try {
        await fetch('/api/configure-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_code: roomCode,
                num_questions: numQuestions,
                difficulty: difficulty,
                include_final_hard_question: includeFinal,
                question_display_time: 5,
                answer_time: answerTime,
                results_display_time: 10,
                voting_time: 15
            }),
        });

        // Start the game
        await fetch('/api/host-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_code: roomCode,
                action: 'start_game'
            }),
        });
    } catch (error) {
        console.error('Error configuring game:', error);
        alert('Could not start game');
    }
}

async function handleAnswerSubmit(e) {
    e.preventDefault();

    const answer = document.getElementById('answer-input').value.trim();
    if (!answer) return;

    try {
        await fetch('/api/submit-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_code: roomCode,
                player_id: playerId,
                answer: answer,
            }),
        });

        document.getElementById('answer-input').value = '';
    } catch (error) {
        console.error('Error submitting answer:', error);
    }
}

async function submitVote(vote) {
    if (!gameState || gameState.disputed_judgement_index === null) return;

    try {
        await fetch('/api/vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_code: roomCode,
                player_id: playerId,
                judgement_index: gameState.disputed_judgement_index,
                vote: vote
            }),
        });

        // Show vote submitted status
        const voteStatus = document.getElementById('vote-status');
        voteStatus.textContent = vote ? '✓ Voted: Close Enough' : '✗ Voted: Nope';
        voteStatus.classList.remove('hidden');
    } catch (error) {
        console.error('Error voting:', error);
    }
}

function updateUI() {
    if (!gameState || !playerId) return;

    // Check if we're the host
    if (gameState.host_id === playerId && !isHost) {
        isHost = true;
        sessionStorage.setItem('isHost', 'true');
    }

    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => screen.classList.add('hidden'));

    // Stop any existing timer
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    // Show appropriate screen
    switch (gameState.phase) {
        case 'lobby':
            showLobbyOrConfig();
            break;
        case 'question':
            showQuestionPreview();
            break;
        case 'answering':
            showAnsweringPhase();
            break;
        case 'judging':
            showJudgingPhase();
            break;
        case 'voting':
            showVotingPhase();
            break;
        case 'results':
            showResultsPhase();
            break;
        case 'final_scores':
            showFinalScores();
            break;
    }
}

function showLobbyOrConfig() {
    if (isHost && Object.keys(gameState.players).length === 0) {
        // Host hasn't joined yet, show config
        document.getElementById('config-screen').classList.remove('hidden');
    } else {
        // Show waiting screen
        document.getElementById('waiting-screen').classList.remove('hidden');
        document.getElementById('player-name-display').textContent = playerName;

        const player = gameState.players[playerId];
        if (player) {
            document.getElementById('lobby-score').textContent = player.score;
        }

        // Update waiting text for host
        if (isHost) {
            document.getElementById('waiting-text').textContent = 'Click START GAME when ready!';
        }
    }
}

function showQuestionPreview() {
    document.getElementById('question-display-screen').classList.remove('hidden');

    const currentQuestion = gameState.questions[gameState.current_question_index];
    const questionNum = gameState.current_question_index + 1;

    document.getElementById('q-num-preview').textContent =
        `Question ${questionNum} of ${gameState.questions.length}`;
    document.getElementById('question-preview').textContent = currentQuestion.text;

    // Start countdown timer
    startPreviewCountdown();
}

function showAnsweringPhase() {
    const player = gameState.players[playerId];
    if (!player) return;

    if (player.answer_submitted) {
        // Already submitted
        showSubmittedScreen();
    } else {
        // Show answer input
        document.getElementById('answer-screen').classList.remove('hidden');

        const currentQuestion = gameState.questions[gameState.current_question_index];
        const questionNum = gameState.current_question_index + 1;

        document.getElementById('q-num-answer').textContent =
            `Question ${questionNum} of ${gameState.questions.length}`;
        document.getElementById('question-text-player').textContent = currentQuestion.text;

        // Focus input
        setTimeout(() => {
            document.getElementById('answer-input').focus();
        }, 100);

        // Start answer timer
        startAnswerTimer();
    }
}

function showSubmittedScreen() {
    document.getElementById('submitted-screen').classList.remove('hidden');

    const player = gameState.players[playerId];
    if (player && player.current_answer) {
        document.getElementById('submitted-answer-text').textContent = player.current_answer;
    }
}

function showJudgingPhase() {
    document.getElementById('judging-screen').classList.remove('hidden');
}

function showVotingPhase() {
    if (!gameState.disputed_judgement_index === null) return;

    const judgement = gameState.current_judgements[gameState.disputed_judgement_index];

    // Don't let player vote on their own answer
    if (judgement.player_id === playerId) {
        showResultsPhase();
        return;
    }

    document.getElementById('voting-screen').classList.remove('hidden');

    const currentQuestion = gameState.questions[gameState.current_question_index];

    document.getElementById('disputed-player-name').textContent = judgement.player_name;
    document.getElementById('disputed-answer-text').textContent = judgement.answer;
    document.getElementById('correct-answer-voting').textContent = currentQuestion.correct_answer;
    document.getElementById('vote-reasoning').textContent = judgement.reasoning;

    // Reset vote status
    document.getElementById('vote-status').classList.add('hidden');

    // Check if already voted
    if (judgement.votes_to_accept[playerId] !== undefined) {
        const voteStatus = document.getElementById('vote-status');
        voteStatus.textContent = judgement.votes_to_accept[playerId] ?
            '✓ Voted: Close Enough' : '✗ Voted: Nope';
        voteStatus.classList.remove('hidden');
    }

    // Start voting timer
    startVotingTimer();
}

function showResultsPhase() {
    document.getElementById('player-results-screen').classList.remove('hidden');

    const currentQuestion = gameState.questions[gameState.current_question_index];
    const myJudgement = gameState.current_judgements.find(j => j.player_id === playerId);

    document.getElementById('correct-answer-player').textContent = currentQuestion.correct_answer;

    if (myJudgement) {
        const resultStatus = document.getElementById('result-status');
        const pointsEarned = document.getElementById('points-earned');

        if (myJudgement.is_correct) {
            resultStatus.textContent = '🎉 CORRECT!';
            resultStatus.className = 'result-status correct';
            pointsEarned.textContent = `+${myJudgement.points_awarded} pts`;
            pointsEarned.className = 'points-earned positive';
        } else {
            resultStatus.textContent = '❌ INCORRECT';
            resultStatus.className = 'result-status incorrect';
            pointsEarned.textContent = '+0 pts';
            pointsEarned.className = 'points-earned zero';
        }

        const judgementBox = document.getElementById('player-judgement');
        judgementBox.innerHTML = `
            <div class="your-answer">Your answer: "${myJudgement.answer}"</div>
            <div class="reasoning">${myJudgement.reasoning}</div>
        `;
    }

    const player = gameState.players[playerId];
    if (player) {
        document.getElementById('current-score').textContent = player.score;
    }
}

function showFinalScores() {
    document.getElementById('player-final-screen').classList.remove('hidden');

    const player = gameState.players[playerId];
    if (!player) return;

    // Calculate placement
    const sortedPlayers = Object.values(gameState.players).sort((a, b) => b.score - a.score);
    const myIndex = sortedPlayers.findIndex(p => p.id === playerId);

    let placementText = '';
    if (myIndex === 0) {
        placementText = '🥇 1ST PLACE!';
    } else if (myIndex === 1) {
        placementText = '🥈 2ND PLACE!';
    } else if (myIndex === 2) {
        placementText = '🥉 3RD PLACE!';
    } else {
        placementText = `#${myIndex + 1}`;
    }

    document.getElementById('final-placement').textContent = placementText;
    document.getElementById('final-score').textContent = player.score;
}

// Timer Functions
function startPreviewCountdown() {
    if (!gameState || !gameState.phase_start_time) return;

    const countdownEl = document.getElementById('preview-countdown');
    const duration = gameState.config.question_display_time;

    timerInterval = setInterval(() => {
        const elapsed = (Date.now() / 1000) - gameState.phase_start_time;
        const remaining = Math.max(0, Math.ceil(duration - elapsed));

        countdownEl.textContent = remaining;

        if (remaining <= 0) {
            clearInterval(timerInterval);
        }
    }, 100);
}

function startAnswerTimer() {
    if (!gameState || !gameState.phase_start_time) return;

    const timerBar = document.getElementById('answer-timer-bar');
    const timerText = document.getElementById('answer-timer-text');
    const duration = gameState.config.answer_time;

    timerInterval = setInterval(() => {
        const elapsed = (Date.now() / 1000) - gameState.phase_start_time;
        const remaining = Math.max(0, duration - elapsed);
        const percentage = (remaining / duration) * 100;

        timerBar.style.width = `${percentage}%`;
        timerText.textContent = `${Math.ceil(remaining)}s`;

        if (remaining <= 0) {
            clearInterval(timerInterval);
        }
    }, 100);
}

function startVotingTimer() {
    if (!gameState || !gameState.phase_start_time) return;

    const timerBar = document.getElementById('vote-timer-bar');
    const timerText = document.getElementById('vote-timer-text');
    const duration = gameState.config.voting_time;

    timerInterval = setInterval(() => {
        const elapsed = (Date.now() / 1000) - gameState.phase_start_time;
        const remaining = Math.max(0, duration - elapsed);
        const percentage = (remaining / duration) * 100;

        timerBar.style.width = `${percentage}%`;
        timerText.textContent = `${Math.ceil(remaining)}s`;

        if (remaining <= 0) {
            clearInterval(timerInterval);
        }
    }, 100);
}
