# flashcards/tests/test_services_group.py
from django.test import TestCase
from flashcards.services.group_service import GroupService
from flashcards.models import Flashcard


class GroupServiceTest(TestCase):
    """
    Testy jednostkowe serwisu GroupService.
    """

    def setUp(self):
        Flashcard.objects.create(question="Q1", answer="A1", category="Science")
        Flashcard.objects.create(question="Q2", answer="A2", category="Math")
        Flashcard.objects.create(question="Q3", answer="A3", category="")
        Flashcard.objects.create(question="Q4", answer="A4", category="")

    def test_get_categories(self):
        categories = GroupService.get_categories()
        expected = ["General", "Math", "Science"]
        self.assertEqual(categories, sorted(expected))

    def test_get_flashcards_by_category_science(self):
        flashcards = GroupService.get_flashcards_by_category("Science")
        self.assertEqual(flashcards.count(), 1)
        self.assertEqual(flashcards.first().question, "Q1")

    def test_get_flashcards_by_category_general(self):
        flashcards = GroupService.get_flashcards_by_category("General")
        self.assertEqual(flashcards.count(), 2)
        questions = flashcards.values_list("question", flat=True)
        self.assertIn("Q3", questions)
        self.assertIn("Q4", questions)

    def test_get_flashcards_by_nonexistent_category(self):
        flashcards = GroupService.get_flashcards_by_category("History")
        self.assertEqual(flashcards.count(), 0)
