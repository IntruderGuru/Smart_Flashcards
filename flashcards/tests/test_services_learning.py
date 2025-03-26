# flashcards/tests/test_services_learning.py
from django.test import TestCase
from unittest.mock import patch
from flashcards.services.learning_service import LearningService
from flashcards.models import Flashcard


class LearningServiceTest(TestCase):
    """
    Testy jednostkowe logiki dobierania kolejnej fiszki w LearningService.
    """

    def setUp(self):
        self.flashcard1 = Flashcard.objects.create(
            question="Q1",
            answer="A1",
            category="Cat1",
            correct_answers=3,
            incorrect_answers=1,
        )
        self.flashcard2 = Flashcard.objects.create(
            question="Q2",
            answer="A2",
            category="Cat1",
            correct_answers=2,
            incorrect_answers=3,
        )
        self.flashcard3 = Flashcard.objects.create(
            question="Q3",
            answer="A3",
            category="Cat1",
            correct_answers=0,
            incorrect_answers=5,
        )

    @patch("flashcards.services.learning_service.random.uniform")
    def test_get_next_flashcard(self, mock_uniform):
        mock_uniform.side_effect = [0.9, 0.3, 0.1]

        flashcards = Flashcard.objects.all()
        next_flashcard = LearningService.get_next_flashcard(flashcards)
        self.assertEqual(next_flashcard, self.flashcard3)

        next_flashcard = LearningService.get_next_flashcard(flashcards)
        self.assertEqual(next_flashcard, self.flashcard2)

        next_flashcard = LearningService.get_next_flashcard(flashcards)
        self.assertEqual(next_flashcard, self.flashcard1)
