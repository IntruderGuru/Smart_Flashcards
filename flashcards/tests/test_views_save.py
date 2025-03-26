# flashcards/tests/test_views_save.py
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from flashcards.models import Flashcard


class SaveFlashcardsViewTest(TestCase):
    """
    Testy widoku zapisu fiszek z pamięci sesji (SaveFlashcardsView).
    """

    def setUp(self):
        self.save_url = reverse("flashcards:save_flashcards")
        self.temp_flashcards = [
            {
                "id": 0,
                "question": "What is Python?",
                "answer": "A programming language.",
                "category": "Programming",
            },
            {
                "id": 1,
                "question": "What is Django?",
                "answer": "A Python web framework.",
                "category": "Programming",
            },
        ]
        session = self.client.session
        session["temp_flashcards"] = self.temp_flashcards
        session.save()

    @patch("flashcards.models.Flashcard.objects.create")
    def test_save_flashcards_view_post_selected_flashcards(self, mock_create):
        data = {
            "flashcard_ids": ["0"],
            "question_0": "What is Python?",
            "answer_0": "A programming language.",
            "category_select_0": "Programming",
        }
        response = self.client.post(self.save_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("flashcards:flashcard_list"))
        mock_create.assert_called_once_with(
            question="What is Python?",
            answer="A programming language.",
            category="Programming",
        )
        self.assertNotIn("temp_flashcards", self.client.session)

    @patch("flashcards.models.Flashcard.objects.create")
    def test_save_flashcards_view_post_no_selection(self, mock_create):
        data = {
            "flashcard_ids": [],
        }
        response = self.client.post(self.save_url, data, follow=True)
        self.assertRedirects(response, reverse("flashcards:flashcard_list"))
        mock_create.assert_not_called()
        self.assertNotIn("temp_flashcards", self.client.session)

    def test_save_flashcards_view_get_method(self):
        response = self.client.get(self.save_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("flashcards:generate_from_text"))
        messages = list(response.context["messages"])
        self.assertEqual(str(messages[0]), "Invalid request method.")
