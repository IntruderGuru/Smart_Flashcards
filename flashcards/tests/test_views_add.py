# flashcards/tests/test_views_add.py
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.contrib.messages import get_messages
from flashcards.models import Flashcard
from flashcards.forms import FlashcardForm


class AddFlashcardViewTest(TestCase):
    """
    Testy widoku dodawania nowej fiszki (AddFlashcardView).
    """

    def setUp(self):
        self.add_url = reverse("flashcards:add_flashcard")

    def test_add_flashcard_view_get(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/add_flashcard.html")
        self.assertIsInstance(response.context["form"], FlashcardForm)

    @patch(
        "flashcards.forms.GroupService.get_categories",
        return_value=["Technology", "Science", "Math"],
    )
    def test_add_flashcard_view_post_valid_data(self, mock_get_categories):
        data = {
            "question": "What is Django?",
            "answer": "A Python web framework.",
            "source": "",
            "category_select": "Technology",
        }
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("flashcards:flashcard_list"))
        self.assertTrue(Flashcard.objects.filter(question="What is Django?").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Flashcard has been successfully added.")

    def test_add_flashcard_view_post_invalid_data(self):
        data = {
            "question": "",
            "answer": "A Python web framework.",
            "category_select": "Technology",
        }
        response = self.client.post(self.add_url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertTrue(form.errors)
        self.assertIn("question", form.errors)
