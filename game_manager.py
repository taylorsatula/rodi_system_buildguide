import random
import string
import time
from typing import Dict, Optional
from models import GameState, Player, Question, GamePhase, JudgementResult
from llm_judge import LLMJudge
from database import trivia_db


class GameManager:
    def __init__(self):
        self.rooms: Dict[str, GameState] = {}
        self.llm_judge = LLMJudge()
        self.questions_per_game = 8  # Number of questions per game session

    def generate_room_code(self) -> str:
        """Generate a 4-letter room code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase, k=4))
            if code not in self.rooms:
                return code

    def create_room(self, host_id: str) -> str:
        """Create a new game room and return the room code"""
        room_code = self.generate_room_code()

        # Create room with default config - questions will be loaded when game starts
        self.rooms[room_code] = GameState(
            room_code=room_code,
            host_id=host_id,
            questions=[]
        )
        return room_code

    def configure_game(
        self,
        room_code: str,
        num_questions: int,
        difficulty: Optional[str],
        include_final: bool,
        question_display_time: int = 5,
        answer_time: int = 30,
        results_display_time: int = 10,
        voting_time: int = 15
    ) -> bool:
        """Configure game settings before starting"""
        room = self.get_room(room_code)
        if not room or room.phase != GamePhase.LOBBY:
            return False

        from models import GameConfig
        room.config = GameConfig(
            num_questions=num_questions,
            difficulty=difficulty,
            include_final_hard_question=include_final,
            question_display_time=question_display_time,
            answer_time=answer_time,
            results_display_time=results_display_time,
            voting_time=voting_time
        )
        return True

    def load_questions_for_game(self, room_code: str) -> bool:
        """Load questions based on game configuration"""
        room = self.get_room(room_code)
        if not room:
            return False

        config = room.config
        questions = []

        try:
            # Load regular questions
            regular_count = config.num_questions - (1 if config.include_final_hard_question else 0)
            if regular_count > 0:
                questions = trivia_db.get_random_questions(
                    count=regular_count,
                    difficulty=config.difficulty
                )

            # Add final hard question if requested
            if config.include_final_hard_question:
                hard_questions = trivia_db.get_random_questions(
                    count=1,
                    difficulty="hard",
                    exclude_ids=set()
                )
                if hard_questions:
                    final_q = hard_questions[0]
                    final_q.is_final_question = True
                    final_q.points = 500  # Bonus points for final question
                    questions.append(final_q)

            # Fallback if database fails
            if not questions:
                questions = self.get_fallback_questions()

            room.questions = questions
            return True

        except Exception as e:
            print(f"Error loading questions: {e}")
            room.questions = self.get_fallback_questions()
            return True

    def get_room(self, room_code: str) -> Optional[GameState]:
        """Get a room by code"""
        return self.rooms.get(room_code)

    def set_phase(self, room: GameState, phase: GamePhase):
        """Set the game phase and record the start time"""
        room.phase = phase
        room.phase_start_time = time.time()

    def check_all_players_answered(self, room: GameState) -> bool:
        """Check if all players have submitted their answers"""
        if not room.players:
            return False
        return all(player.answer_submitted for player in room.players.values())

    def add_player(self, room_code: str, player_id: str, player_name: str) -> bool:
        """Add a player to a room"""
        room = self.get_room(room_code)
        if not room or room.phase != GamePhase.LOBBY:
            return False

        room.players[player_id] = Player(id=player_id, name=player_name)
        return True

    def submit_answer(self, room_code: str, player_id: str, answer: str) -> bool:
        """Submit an answer for a player"""
        room = self.get_room(room_code)
        if not room or room.phase != GamePhase.ANSWERING:
            return False

        player = room.players.get(player_id)
        if not player:
            return False

        player.current_answer = answer
        player.answer_submitted = True
        return True

    def start_game(self, room_code: str) -> bool:
        """Start the game"""
        room = self.get_room(room_code)
        if not room or room.phase != GamePhase.LOBBY:
            return False

        # Load questions based on configuration
        self.load_questions_for_game(room_code)

        room.current_question_index = 0
        self.set_phase(room, GamePhase.QUESTION)
        return True

    def start_answering(self, room_code: str) -> bool:
        """Start the answering phase"""
        room = self.get_room(room_code)
        if not room:
            return False

        # Reset all players' answer status
        for player in room.players.values():
            player.current_answer = None
            player.answer_submitted = False

        self.set_phase(room, GamePhase.ANSWERING)
        return True

    async def judge_answers(self, room_code: str) -> bool:
        """Judge all submitted answers"""
        room = self.get_room(room_code)
        if not room or room.phase != GamePhase.ANSWERING:
            return False

        self.set_phase(room, GamePhase.JUDGING)
        room.current_judgements = []

        current_question = room.questions[room.current_question_index]

        # Judge each player's answer
        for player in room.players.values():
            if player.answer_submitted and player.current_answer:
                judgement = await self.llm_judge.judge_answer(
                    player_id=player.id,
                    player_name=player.name,
                    question=current_question.text,
                    correct_answer=current_question.correct_answer,
                    player_answer=player.current_answer,
                    points=current_question.points
                )

                # Update player score
                player.score += judgement.points_awarded
                room.current_judgements.append(judgement)
            else:
                # Player didn't answer
                room.current_judgements.append(JudgementResult(
                    player_id=player.id,
                    player_name=player.name,
                    answer="(No answer submitted)",
                    is_correct=False,
                    points_awarded=0,
                    reasoning="No answer was submitted in time"
                ))

        self.set_phase(room, GamePhase.RESULTS)
        return True

    def start_voting(self, room_code: str, judgement_index: int) -> bool:
        """Start a vote on a disputed answer"""
        room = self.get_room(room_code)
        if not room or room.phase != GamePhase.RESULTS:
            return False

        if judgement_index < 0 or judgement_index >= len(room.current_judgements):
            return False

        # Only allow voting on incorrect answers with reasoning
        judgement = room.current_judgements[judgement_index]
        if judgement.is_correct:
            return False

        room.disputed_judgement_index = judgement_index
        self.set_phase(room, GamePhase.VOTING)
        return True

    def submit_vote(self, room_code: str, player_id: str, judgement_index: int, vote: bool) -> bool:
        """Submit a vote for a disputed answer"""
        room = self.get_room(room_code)
        if not room or room.phase != GamePhase.VOTING:
            return False

        if room.disputed_judgement_index != judgement_index:
            return False

        judgement = room.current_judgements[judgement_index]

        # Don't let the player vote on their own answer
        if judgement.player_id == player_id:
            return False

        # Record vote
        judgement.votes_to_accept[player_id] = vote
        return True

    def finish_voting(self, room_code: str) -> bool:
        """Finish voting and apply the result"""
        room = self.get_room(room_code)
        if not room or room.phase != GamePhase.VOTING:
            return False

        if room.disputed_judgement_index is None:
            return False

        judgement = room.current_judgements[room.disputed_judgement_index]

        # Count votes
        yes_votes = sum(1 for v in judgement.votes_to_accept.values() if v)
        total_votes = len(judgement.votes_to_accept)

        # Majority wins
        if total_votes > 0:
            judgement.vote_result = yes_votes > (total_votes / 2)

            # If majority accepted, award points
            if judgement.vote_result:
                player = room.players.get(judgement.player_id)
                if player:
                    current_question = room.questions[room.current_question_index]
                    judgement.points_awarded = current_question.points
                    player.score += judgement.points_awarded
                    judgement.is_correct = True  # Mark as correct due to vote
        else:
            judgement.vote_result = False

        # Return to results
        self.set_phase(room, GamePhase.RESULTS)
        room.disputed_judgement_index = None
        return True

    def next_question(self, room_code: str) -> bool:
        """Move to the next question or end the game"""
        room = self.get_room(room_code)
        if not room:
            return False

        room.current_question_index += 1

        if room.current_question_index >= len(room.questions):
            self.set_phase(room, GamePhase.FINAL_SCORES)
        else:
            self.set_phase(room, GamePhase.QUESTION)

        return True

    async def check_auto_advance(self, room_code: str) -> bool:
        """Check if the game should auto-advance and do so if needed"""
        room = self.get_room(room_code)
        if not room or not room.auto_advance_enabled or room.phase_start_time is None:
            return False

        current_time = time.time()
        elapsed = current_time - room.phase_start_time

        # Handle auto-advance based on current phase
        if room.phase == GamePhase.QUESTION:
            # Auto-start answering after question display time
            if elapsed >= room.config.question_display_time:
                self.start_answering(room_code)
                return True

        elif room.phase == GamePhase.ANSWERING:
            # Auto-judge if all players answered OR timeout reached
            if self.check_all_players_answered(room) or elapsed >= room.config.answer_time:
                await self.judge_answers(room_code)
                return True

        elif room.phase == GamePhase.RESULTS:
            # Auto-advance to next question after results display time
            if elapsed >= room.config.results_display_time:
                self.next_question(room_code)
                return True

        elif room.phase == GamePhase.VOTING:
            # Auto-finish voting after voting time
            if elapsed >= room.config.voting_time:
                self.finish_voting(room_code)
                return True

        return False

    def get_fallback_questions(self) -> list[Question]:
        """Return a fallback set of trivia questions when database is unavailable"""
        return [
            Question(
                text="What is the capital of France?",
                correct_answer="Paris",
                category="Geography",
                points=100
            ),
            Question(
                text="Who painted the Mona Lisa?",
                correct_answer="Leonardo da Vinci",
                category="Art",
                points=100
            ),
            Question(
                text="What is the largest planet in our solar system?",
                correct_answer="Jupiter",
                category="Science",
                points=100
            ),
            Question(
                text="In what year did World War II end?",
                correct_answer="1945",
                category="History",
                points=100
            ),
            Question(
                text="What is the chemical symbol for gold?",
                correct_answer="Au",
                category="Science",
                points=100
            ),
            Question(
                text="Who wrote 'Romeo and Juliet'?",
                correct_answer="William Shakespeare",
                category="Literature",
                points=100
            ),
            Question(
                text="What is the smallest country in the world?",
                correct_answer="Vatican City",
                category="Geography",
                points=100
            ),
            Question(
                text="How many strings does a standard guitar have?",
                correct_answer="Six",
                category="Music",
                points=100
            ),
        ]


# Global game manager instance
game_manager = GameManager()
