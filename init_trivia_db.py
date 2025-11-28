#!/usr/bin/env python3
"""
Initialize the trivia database with a comprehensive set of questions.

This script populates the database with trivia questions across multiple categories.
Questions are sourced from public domain and creative commons sources.
"""

from database import trivia_db

# Comprehensive trivia questions across multiple categories
TRIVIA_QUESTIONS = [
    # Geography Questions
    {"text": "What is the capital of France?", "correct_answer": "Paris", "category": "Geography", "difficulty": "easy", "points": 100, "source": "General Knowledge"},
    {"text": "What is the largest country in the world by area?", "correct_answer": "Russia", "category": "Geography", "difficulty": "easy", "points": 100, "source": "General Knowledge"},
    {"text": "Which river is the longest in the world?", "correct_answer": "Nile River", "category": "Geography", "difficulty": "medium", "points": 100, "source": "General Knowledge"},
    {"text": "What is the smallest country in the world?", "correct_answer": "Vatican City", "category": "Geography", "difficulty": "medium", "points": 100, "source": "General Knowledge"},
    {"text": "In which country would you find the ancient city of Petra?", "correct_answer": "Jordan", "category": "Geography", "difficulty": "medium", "points": 100, "source": "General Knowledge"},
    {"text": "What is the capital of Australia?", "correct_answer": "Canberra", "category": "Geography", "difficulty": "medium", "points": 100, "source": "General Knowledge"},
    {"text": "Which ocean is the largest?", "correct_answer": "Pacific Ocean", "category": "Geography", "difficulty": "easy", "points": 100, "source": "General Knowledge"},
    {"text": "What is the highest mountain in the world?", "correct_answer": "Mount Everest", "category": "Geography", "difficulty": "easy", "points": 100, "source": "General Knowledge"},
    {"text": "Which desert is the largest in the world?", "correct_answer": "Antarctic Desert", "category": "Geography", "difficulty": "hard", "points": 100, "source": "General Knowledge"},
    {"text": "What is the capital of Canada?", "correct_answer": "Ottawa", "category": "Geography", "difficulty": "medium", "points": 100, "source": "General Knowledge"},

    # Science Questions
    {"text": "What is the chemical symbol for gold?", "correct_answer": "Au", "category": "Science", "difficulty": "easy", "points": 100, "source": "Chemistry"},
    {"text": "What is the largest planet in our solar system?", "correct_answer": "Jupiter", "category": "Science", "difficulty": "easy", "points": 100, "source": "Astronomy"},
    {"text": "What is the speed of light in a vacuum?", "correct_answer": "299,792,458 meters per second", "category": "Science", "difficulty": "hard", "points": 100, "source": "Physics"},
    {"text": "What is the atomic number of carbon?", "correct_answer": "6", "category": "Science", "difficulty": "medium", "points": 100, "source": "Chemistry"},
    {"text": "Who developed the theory of relativity?", "correct_answer": "Albert Einstein", "category": "Science", "difficulty": "easy", "points": 100, "source": "Physics"},
    {"text": "What is the smallest unit of life?", "correct_answer": "Cell", "category": "Science", "difficulty": "easy", "points": 100, "source": "Biology"},
    {"text": "What is the chemical formula for water?", "correct_answer": "H2O", "category": "Science", "difficulty": "easy", "points": 100, "source": "Chemistry"},
    {"text": "How many bones are in the adult human body?", "correct_answer": "206", "category": "Science", "difficulty": "medium", "points": 100, "source": "Biology"},
    {"text": "What is the boiling point of water at sea level in Celsius?", "correct_answer": "100 degrees Celsius", "category": "Science", "difficulty": "easy", "points": 100, "source": "Chemistry"},
    {"text": "What planet is known as the Red Planet?", "correct_answer": "Mars", "category": "Science", "difficulty": "easy", "points": 100, "source": "Astronomy"},
    {"text": "What is the powerhouse of the cell?", "correct_answer": "Mitochondria", "category": "Science", "difficulty": "medium", "points": 100, "source": "Biology"},
    {"text": "What element has the chemical symbol Fe?", "correct_answer": "Iron", "category": "Science", "difficulty": "easy", "points": 100, "source": "Chemistry"},

    # History Questions
    {"text": "In what year did World War II end?", "correct_answer": "1945", "category": "History", "difficulty": "easy", "points": 100, "source": "World History"},
    {"text": "Who was the first President of the United States?", "correct_answer": "George Washington", "category": "History", "difficulty": "easy", "points": 100, "source": "US History"},
    {"text": "In which year did Christopher Columbus reach the Americas?", "correct_answer": "1492", "category": "History", "difficulty": "medium", "points": 100, "source": "World History"},
    {"text": "Who was the first person to walk on the moon?", "correct_answer": "Neil Armstrong", "category": "History", "difficulty": "easy", "points": 100, "source": "Modern History"},
    {"text": "What year did the Berlin Wall fall?", "correct_answer": "1989", "category": "History", "difficulty": "medium", "points": 100, "source": "Modern History"},
    {"text": "Who was the ancient Egyptian queen who had a relationship with Julius Caesar and Mark Antony?", "correct_answer": "Cleopatra", "category": "History", "difficulty": "easy", "points": 100, "source": "Ancient History"},
    {"text": "What year did the Titanic sink?", "correct_answer": "1912", "category": "History", "difficulty": "medium", "points": 100, "source": "Modern History"},
    {"text": "Who painted the ceiling of the Sistine Chapel?", "correct_answer": "Michelangelo", "category": "History", "difficulty": "medium", "points": 100, "source": "Art History"},
    {"text": "What was the name of the ship that brought the Pilgrims to America?", "correct_answer": "Mayflower", "category": "History", "difficulty": "medium", "points": 100, "source": "US History"},
    {"text": "In what year did World War I begin?", "correct_answer": "1914", "category": "History", "difficulty": "medium", "points": 100, "source": "World History"},

    # Literature Questions
    {"text": "Who wrote 'Romeo and Juliet'?", "correct_answer": "William Shakespeare", "category": "Literature", "difficulty": "easy", "points": 100, "source": "Classic Literature"},
    {"text": "Who wrote '1984'?", "correct_answer": "George Orwell", "category": "Literature", "difficulty": "medium", "points": 100, "source": "Modern Literature"},
    {"text": "What is the first book in the Harry Potter series?", "correct_answer": "Harry Potter and the Philosopher's Stone", "category": "Literature", "difficulty": "easy", "points": 100, "source": "Modern Literature"},
    {"text": "Who wrote 'To Kill a Mockingbird'?", "correct_answer": "Harper Lee", "category": "Literature", "difficulty": "medium", "points": 100, "source": "Modern Literature"},
    {"text": "Who wrote 'Pride and Prejudice'?", "correct_answer": "Jane Austen", "category": "Literature", "difficulty": "medium", "points": 100, "source": "Classic Literature"},
    {"text": "What is the name of the hobbit in 'The Lord of the Rings'?", "correct_answer": "Frodo Baggins", "category": "Literature", "difficulty": "easy", "points": 100, "source": "Fantasy Literature"},
    {"text": "Who wrote 'The Great Gatsby'?", "correct_answer": "F. Scott Fitzgerald", "category": "Literature", "difficulty": "medium", "points": 100, "source": "Modern Literature"},
    {"text": "Who wrote 'Moby Dick'?", "correct_answer": "Herman Melville", "category": "Literature", "difficulty": "medium", "points": 100, "source": "Classic Literature"},
    {"text": "What is the name of Sherlock Holmes' companion?", "correct_answer": "Dr. Watson", "category": "Literature", "difficulty": "easy", "points": 100, "source": "Classic Literature"},
    {"text": "Who wrote 'The Catcher in the Rye'?", "correct_answer": "J.D. Salinger", "category": "Literature", "difficulty": "medium", "points": 100, "source": "Modern Literature"},

    # Music Questions
    {"text": "How many strings does a standard guitar have?", "correct_answer": "Six", "category": "Music", "difficulty": "easy", "points": 100, "source": "General Music"},
    {"text": "Who is known as the 'King of Pop'?", "correct_answer": "Michael Jackson", "category": "Music", "difficulty": "easy", "points": 100, "source": "Pop Music"},
    {"text": "What is the highest female singing voice?", "correct_answer": "Soprano", "category": "Music", "difficulty": "medium", "points": 100, "source": "Classical Music"},
    {"text": "Which band released the album 'Abbey Road'?", "correct_answer": "The Beatles", "category": "Music", "difficulty": "easy", "points": 100, "source": "Rock Music"},
    {"text": "What instrument has 88 keys?", "correct_answer": "Piano", "category": "Music", "difficulty": "easy", "points": 100, "source": "General Music"},
    {"text": "Who composed 'The Four Seasons'?", "correct_answer": "Antonio Vivaldi", "category": "Music", "difficulty": "medium", "points": 100, "source": "Classical Music"},
    {"text": "What is the lowest male singing voice?", "correct_answer": "Bass", "category": "Music", "difficulty": "medium", "points": 100, "source": "Classical Music"},
    {"text": "Which classical composer was deaf?", "correct_answer": "Ludwig van Beethoven", "category": "Music", "difficulty": "easy", "points": 100, "source": "Classical Music"},
    {"text": "What does 'forte' mean in music?", "correct_answer": "Loud", "category": "Music", "difficulty": "medium", "points": 100, "source": "Music Theory"},
    {"text": "Which band sang 'Bohemian Rhapsody'?", "correct_answer": "Queen", "category": "Music", "difficulty": "easy", "points": 100, "source": "Rock Music"},

    # Sports Questions
    {"text": "How many players are on a soccer team?", "correct_answer": "11", "category": "Sports", "difficulty": "easy", "points": 100, "source": "Soccer"},
    {"text": "In which sport would you perform a slam dunk?", "correct_answer": "Basketball", "category": "Sports", "difficulty": "easy", "points": 100, "source": "Basketball"},
    {"text": "How many bases are there on a baseball field?", "correct_answer": "Four", "category": "Sports", "difficulty": "easy", "points": 100, "source": "Baseball"},
    {"text": "What is the maximum score in a single frame of bowling?", "correct_answer": "30", "category": "Sports", "difficulty": "medium", "points": 100, "source": "Bowling"},
    {"text": "In which sport would you use a puck?", "correct_answer": "Ice Hockey", "category": "Sports", "difficulty": "easy", "points": 100, "source": "Ice Hockey"},
    {"text": "How long is a marathon in miles?", "correct_answer": "26.2 miles", "category": "Sports", "difficulty": "medium", "points": 100, "source": "Track and Field"},
    {"text": "What sport is known as 'the beautiful game'?", "correct_answer": "Soccer", "category": "Sports", "difficulty": "easy", "points": 100, "source": "Soccer"},
    {"text": "In tennis, what is a score of zero called?", "correct_answer": "Love", "category": "Sports", "difficulty": "medium", "points": 100, "source": "Tennis"},
    {"text": "How many rings are on the Olympic flag?", "correct_answer": "Five", "category": "Sports", "difficulty": "easy", "points": 100, "source": "Olympics"},
    {"text": "What is the diameter of a basketball hoop in inches?", "correct_answer": "18 inches", "category": "Sports", "difficulty": "hard", "points": 100, "source": "Basketball"},

    # Movies & TV Questions
    {"text": "Who directed 'Jurassic Park'?", "correct_answer": "Steven Spielberg", "category": "Movies", "difficulty": "medium", "points": 100, "source": "Cinema"},
    {"text": "What is the highest-grossing film of all time (not adjusted for inflation)?", "correct_answer": "Avatar", "category": "Movies", "difficulty": "medium", "points": 100, "source": "Cinema"},
    {"text": "Who played Iron Man in the Marvel Cinematic Universe?", "correct_answer": "Robert Downey Jr.", "category": "Movies", "difficulty": "easy", "points": 100, "source": "Cinema"},
    {"text": "What year was the first Star Wars movie released?", "correct_answer": "1977", "category": "Movies", "difficulty": "medium", "points": 100, "source": "Cinema"},
    {"text": "Who played Jack in the movie 'Titanic'?", "correct_answer": "Leonardo DiCaprio", "category": "Movies", "difficulty": "easy", "points": 100, "source": "Cinema"},
    {"text": "What is the name of the fictional African country in 'Black Panther'?", "correct_answer": "Wakanda", "category": "Movies", "difficulty": "easy", "points": 100, "source": "Cinema"},
    {"text": "Who directed 'The Dark Knight' trilogy?", "correct_answer": "Christopher Nolan", "category": "Movies", "difficulty": "medium", "points": 100, "source": "Cinema"},
    {"text": "What is the name of the wizarding school in Harry Potter?", "correct_answer": "Hogwarts", "category": "Movies", "difficulty": "easy", "points": 100, "source": "Cinema"},
    {"text": "Which actor played James Bond in 'Casino Royale' (2006)?", "correct_answer": "Daniel Craig", "category": "Movies", "difficulty": "easy", "points": 100, "source": "Cinema"},
    {"text": "What animated movie features the song 'Let It Go'?", "correct_answer": "Frozen", "category": "Movies", "difficulty": "easy", "points": 100, "source": "Cinema"},

    # Art Questions
    {"text": "Who painted the Mona Lisa?", "correct_answer": "Leonardo da Vinci", "category": "Art", "difficulty": "easy", "points": 100, "source": "Art History"},
    {"text": "What style of art is Salvador Dali known for?", "correct_answer": "Surrealism", "category": "Art", "difficulty": "medium", "points": 100, "source": "Art History"},
    {"text": "What is the most expensive painting ever sold?", "correct_answer": "Salvator Mundi", "category": "Art", "difficulty": "hard", "points": 100, "source": "Art Market"},
    {"text": "Who cut off his own ear?", "correct_answer": "Vincent van Gogh", "category": "Art", "difficulty": "medium", "points": 100, "source": "Art History"},
    {"text": "What museum is the Mona Lisa displayed in?", "correct_answer": "The Louvre", "category": "Art", "difficulty": "medium", "points": 100, "source": "Art History"},
    {"text": "Who painted 'Starry Night'?", "correct_answer": "Vincent van Gogh", "category": "Art", "difficulty": "easy", "points": 100, "source": "Art History"},
    {"text": "What is the art technique of painting on wet plaster?", "correct_answer": "Fresco", "category": "Art", "difficulty": "hard", "points": 100, "source": "Art Techniques"},
    {"text": "Who sculpted 'David'?", "correct_answer": "Michelangelo", "category": "Art", "difficulty": "medium", "points": 100, "source": "Art History"},
    {"text": "What color is created by mixing red and blue?", "correct_answer": "Purple", "category": "Art", "difficulty": "easy", "points": 100, "source": "Color Theory"},
    {"text": "Who is known for his soup can paintings?", "correct_answer": "Andy Warhol", "category": "Art", "difficulty": "medium", "points": 100, "source": "Pop Art"},

    # Technology & Computers
    {"text": "Who is the founder of Microsoft?", "correct_answer": "Bill Gates", "category": "Technology", "difficulty": "easy", "points": 100, "source": "Tech History"},
    {"text": "What does HTML stand for?", "correct_answer": "HyperText Markup Language", "category": "Technology", "difficulty": "medium", "points": 100, "source": "Web Development"},
    {"text": "What year was the first iPhone released?", "correct_answer": "2007", "category": "Technology", "difficulty": "medium", "points": 100, "source": "Tech History"},
    {"text": "Who is the founder of Facebook?", "correct_answer": "Mark Zuckerberg", "category": "Technology", "difficulty": "easy", "points": 100, "source": "Tech History"},
    {"text": "What does CPU stand for?", "correct_answer": "Central Processing Unit", "category": "Technology", "difficulty": "easy", "points": 100, "source": "Computer Hardware"},
    {"text": "What programming language is known for its use in web development and has a coffee cup as its logo?", "correct_answer": "Java", "category": "Technology", "difficulty": "medium", "points": 100, "source": "Programming"},
    {"text": "What does AI stand for?", "correct_answer": "Artificial Intelligence", "category": "Technology", "difficulty": "easy", "points": 100, "source": "Computing"},
    {"text": "Who founded Apple Inc. along with Steve Wozniak?", "correct_answer": "Steve Jobs", "category": "Technology", "difficulty": "easy", "points": 100, "source": "Tech History"},
    {"text": "What is the most popular programming language for machine learning?", "correct_answer": "Python", "category": "Technology", "difficulty": "medium", "points": 100, "source": "Programming"},
    {"text": "What year was Google founded?", "correct_answer": "1998", "category": "Technology", "difficulty": "medium", "points": 100, "source": "Tech History"},

    # Food & Drink
    {"text": "What is the main ingredient in guacamole?", "correct_answer": "Avocado", "category": "Food", "difficulty": "easy", "points": 100, "source": "Cooking"},
    {"text": "What type of pasta is shaped like a butterfly?", "correct_answer": "Farfalle", "category": "Food", "difficulty": "medium", "points": 100, "source": "Cooking"},
    {"text": "What country is sushi from?", "correct_answer": "Japan", "category": "Food", "difficulty": "easy", "points": 100, "source": "Cuisine"},
    {"text": "What is the most expensive spice in the world by weight?", "correct_answer": "Saffron", "category": "Food", "difficulty": "hard", "points": 100, "source": "Cooking"},
    {"text": "What is the main ingredient in hummus?", "correct_answer": "Chickpeas", "category": "Food", "difficulty": "medium", "points": 100, "source": "Cooking"},
    {"text": "What fruit is known as the 'king of fruits'?", "correct_answer": "Durian", "category": "Food", "difficulty": "hard", "points": 100, "source": "Fruits"},
    {"text": "What nut is used to make marzipan?", "correct_answer": "Almond", "category": "Food", "difficulty": "medium", "points": 100, "source": "Cooking"},
    {"text": "What country is the origin of the croissant?", "correct_answer": "Austria", "category": "Food", "difficulty": "hard", "points": 100, "source": "Cuisine"},
    {"text": "What is the main ingredient in traditional Japanese miso soup?", "correct_answer": "Miso paste", "category": "Food", "difficulty": "medium", "points": 100, "source": "Cuisine"},
    {"text": "What type of alcohol is made from fermented grapes?", "correct_answer": "Wine", "category": "Food", "difficulty": "easy", "points": 100, "source": "Beverages"},

    # Mythology & Religion
    {"text": "Who is the king of the Greek gods?", "correct_answer": "Zeus", "category": "Mythology", "difficulty": "easy", "points": 100, "source": "Greek Mythology"},
    {"text": "What is the name of Thor's hammer?", "correct_answer": "Mjolnir", "category": "Mythology", "difficulty": "medium", "points": 100, "source": "Norse Mythology"},
    {"text": "Who is the Egyptian god of the dead?", "correct_answer": "Anubis", "category": "Mythology", "difficulty": "medium", "points": 100, "source": "Egyptian Mythology"},
    {"text": "Who is the Roman god of war?", "correct_answer": "Mars", "category": "Mythology", "difficulty": "medium", "points": 100, "source": "Roman Mythology"},
    {"text": "What creature has the head of a lion and the body of a fish in Singapore's mythology?", "correct_answer": "Merlion", "category": "Mythology", "difficulty": "hard", "points": 100, "source": "Asian Mythology"},
    {"text": "In Greek mythology, who flew too close to the sun?", "correct_answer": "Icarus", "category": "Mythology", "difficulty": "easy", "points": 100, "source": "Greek Mythology"},
    {"text": "Who is the Greek goddess of wisdom?", "correct_answer": "Athena", "category": "Mythology", "difficulty": "medium", "points": 100, "source": "Greek Mythology"},
    {"text": "What is the name of the one-eyed giants in Greek mythology?", "correct_answer": "Cyclops", "category": "Mythology", "difficulty": "medium", "points": 100, "source": "Greek Mythology"},
    {"text": "Who is the Norse god of mischief?", "correct_answer": "Loki", "category": "Mythology", "difficulty": "easy", "points": 100, "source": "Norse Mythology"},
    {"text": "What creature is half-man and half-horse?", "correct_answer": "Centaur", "category": "Mythology", "difficulty": "easy", "points": 100, "source": "Greek Mythology"},
]


def main():
    """Initialize the database with trivia questions"""
    print("Initializing trivia database...")

    # Check if database already has questions
    existing_count = trivia_db.get_question_count()
    if existing_count > 0:
        response = input(f"Database already contains {existing_count} questions. Clear and reinitialize? (yes/no): ")
        if response.lower() == 'yes':
            trivia_db.clear_all_questions()
            print("Cleared existing questions.")
        else:
            print("Keeping existing questions and adding new ones.")

    # Add questions in bulk
    count = trivia_db.add_questions_bulk(TRIVIA_QUESTIONS)
    print(f"Successfully added {count} questions to the database!")

    # Display statistics
    total = trivia_db.get_question_count()
    categories = trivia_db.get_categories()

    print(f"\nDatabase Statistics:")
    print(f"Total questions: {total}")
    print(f"Categories: {', '.join(categories)}")

    # Show count per category
    print(f"\nQuestions per category:")
    for category in categories:
        cat_count = trivia_db.get_question_count(category=category)
        print(f"  {category}: {cat_count}")

    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    main()
