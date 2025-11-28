import os
from anthropic import Anthropic
from models import JudgementResult


class LLMJudge:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-haiku-20241022"

    async def judge_answer(
        self,
        player_id: str,
        player_name: str,
        question: str,
        correct_answer: str,
        player_answer: str,
        points: int = 100
    ) -> JudgementResult:
        """
        Use Claude to judge if the player's answer is correct.
        Returns a JudgementResult with scoring and reasoning.
        """

        prompt = f"""You are judging answers for a trivia game.

Question: {question}
Correct Answer: {correct_answer}
Player's Answer: {player_answer}

Determine if the player's answer is correct. Be lenient with:
- Minor spelling mistakes
- Different phrasing that means the same thing
- Partial answers that capture the key information
- Additional context that doesn't contradict the answer

Be strict with:
- Completely wrong information
- Answers that contradict the correct answer
- Random guesses

Respond in this exact format:
CORRECT: yes/no
REASONING: [brief explanation in one sentence]

Example responses:
CORRECT: yes
REASONING: The player provided the correct name despite a minor spelling variation.

CORRECT: no
REASONING: The player's answer refers to a different person/concept entirely."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Parse the response
            lines = response_text.strip().split('\n')
            is_correct = False
            reasoning = "Unable to parse judge response"

            for line in lines:
                if line.startswith("CORRECT:"):
                    is_correct = "yes" in line.lower()
                elif line.startswith("REASONING:"):
                    reasoning = line.replace("REASONING:", "").strip()

            points_awarded = points if is_correct else 0

            return JudgementResult(
                player_id=player_id,
                player_name=player_name,
                answer=player_answer,
                is_correct=is_correct,
                points_awarded=points_awarded,
                reasoning=reasoning
            )

        except Exception as e:
            print(f"Error judging answer: {e}")
            # In case of error, be lenient and give partial credit
            return JudgementResult(
                player_id=player_id,
                player_name=player_name,
                answer=player_answer,
                is_correct=False,
                points_awarded=0,
                reasoning=f"Error during judging: {str(e)}"
            )
