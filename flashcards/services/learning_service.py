import random


class LearningService:
    @staticmethod
    def get_next_flashcard(flashcards):
        """
        Selects the next flashcard for learning, prioritizing ones with lower success rates.
        """
        weighted_flashcards = [
            (flashcard, 1 / (1 + flashcard.correct_answers)) for flashcard in flashcards
        ]
        total_weight = sum(weight for _, weight in weighted_flashcards)
        random_choice = random.uniform(0, total_weight)

        for flashcard, weight in weighted_flashcards:
            random_choice -= weight
            if random_choice <= 0:
                return flashcard
