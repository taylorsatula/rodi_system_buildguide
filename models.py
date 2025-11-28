from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class GamePhase(str, Enum):
    LOBBY = "lobby"
    QUESTION = "question"
    ANSWERING = "answering"
    JUDGING = "judging"
    VOTING = "voting"
    RESULTS = "results"
    FINAL_SCORES = "final_scores"


class Player(BaseModel):
    id: str
    name: str
    score: int = 0
    current_answer: Optional[str] = None
    answer_submitted: bool = False


class Question(BaseModel):
    text: str
    correct_answer: str
    category: Optional[str] = None
    points: int = 100
    is_final_question: bool = False


class JudgementResult(BaseModel):
    player_id: str
    player_name: str
    answer: str
    is_correct: bool
    points_awarded: int
    reasoning: str
    votes_to_accept: Dict[str, bool] = {}  # player_id -> vote (True = accept, False = reject)
    vote_result: Optional[bool] = None  # True if majority voted to accept


class GameConfig(BaseModel):
    num_questions: int = 8
    difficulty: Optional[str] = None  # None = mixed, "easy", "medium", "hard"
    include_final_hard_question: bool = True


class GameState(BaseModel):
    room_code: str
    host_id: str
    players: Dict[str, Player] = {}
    phase: GamePhase = GamePhase.LOBBY
    current_question_index: int = 0
    questions: List[Question] = []
    current_judgements: List[JudgementResult] = []
    round_number: int = 0
    config: GameConfig = GameConfig()
    disputed_judgement_index: Optional[int] = None  # Index of judgement being voted on


class JoinRoomRequest(BaseModel):
    room_code: str
    player_name: str


class SubmitAnswerRequest(BaseModel):
    room_code: str
    player_id: str
    answer: str


class HostActionRequest(BaseModel):
    room_code: str
    action: str  # "start_game", "next_question", "show_results", "end_game", "start_voting"


class ConfigureGameRequest(BaseModel):
    room_code: str
    num_questions: int
    difficulty: Optional[str] = None
    include_final_hard_question: bool = True


class VoteRequest(BaseModel):
    room_code: str
    player_id: str
    judgement_index: int
    vote: bool  # True = accept answer, False = reject answer
