import sqlite3
from typing import List, Set, Optional
from models import Question
import random


class TriviaDatabase:
    def __init__(self, db_path: str = "trivia.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with the required schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                category TEXT,
                difficulty TEXT,
                points INTEGER DEFAULT 100,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on category for faster filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON questions(category)
        """)

        # Create index on difficulty for faster filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_difficulty ON questions(difficulty)
        """)

        conn.commit()
        conn.close()

    def add_question(
        self,
        text: str,
        correct_answer: str,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        points: int = 100,
        source: Optional[str] = None
    ) -> int:
        """Add a new question to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO questions (text, correct_answer, category, difficulty, points, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (text, correct_answer, category, difficulty, points, source))

        question_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return question_id

    def add_questions_bulk(self, questions: List[dict]) -> int:
        """Add multiple questions at once"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.executemany("""
            INSERT INTO questions (text, correct_answer, category, difficulty, points, source)
            VALUES (:text, :correct_answer, :category, :difficulty, :points, :source)
        """, questions)

        count = cursor.rowcount
        conn.commit()
        conn.close()

        return count

    def get_random_questions(
        self,
        count: int,
        exclude_ids: Set[int] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Question]:
        """
        Get random questions from the database with optional filtering.

        Args:
            count: Number of questions to retrieve
            exclude_ids: Set of question IDs to exclude (for avoiding repeats)
            category: Optional category filter
            difficulty: Optional difficulty filter

        Returns:
            List of Question objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build query with filters
        query = "SELECT id, text, correct_answer, category, points FROM questions"
        conditions = []
        params = []

        if exclude_ids:
            placeholders = ','.join('?' * len(exclude_ids))
            conditions.append(f"id NOT IN ({placeholders})")
            params.extend(exclude_ids)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if difficulty:
            conditions.append("difficulty = ?")
            params.append(difficulty)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(count)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        questions = []
        for row in rows:
            questions.append(Question(
                text=row[1],
                correct_answer=row[2],
                category=row[3],
                points=row[4] or 100
            ))

        return questions

    def get_question_count(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> int:
        """Get the total number of questions in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT COUNT(*) FROM questions"
        conditions = []
        params = []

        if category:
            conditions.append("category = ?")
            params.append(category)

        if difficulty:
            conditions.append("difficulty = ?")
            params.append(difficulty)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()

        return count

    def get_categories(self) -> List[str]:
        """Get all unique categories from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT category FROM questions WHERE category IS NOT NULL ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()

        return categories

    def clear_all_questions(self):
        """Remove all questions from the database (use with caution!)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM questions")
        conn.commit()
        conn.close()


# Global database instance
trivia_db = TriviaDatabase()
