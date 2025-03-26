# flashcards/tests/test_views_edit.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from flashcards.models import Flashcard
from flashcards.forms import FlashcardForm


class EditFlashcardViewTest(TestCase):
    """
    Testy widoku edycji fiszki (EditFlashcardView).
    """

    def setUp(self):
        self.flashcard = Flashcard.objects.create(
            question="What is AI?",
            answer="Artificial Intelligence.",
            category="Technology",
        )
        self.edit_url = reverse(
            "flashcards:edit_flashcard", kwargs={"pk": self.flashcard.pk}
        )

    def test_edit_flashcard_view_get(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/edit_flashcard.html")
        self.assertIsInstance(response.context["form"], FlashcardForm)
        self.assertEqual(response.context["form"].instance, self.flashcard)

    def test_edit_flashcard_view_post_valid_data(self):
        data = {
            "question": "What is Machine Learning?",
            "answer": "A subset of AI focused on learning from data.",
            "source": "",
            "category_select": "Technology",
        }
        response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("flashcards:flashcard_list"))
        self.flashcard.refresh_from_db()
        self.assertEqual(self.flashcard.question, "What is Machine Learning?")

    def test_edit_flashcard_view_post_invalid_data(self):
        data = {
            "question": "",
            "answer": "A subset of AI focused on learning from data.",
            "source": "",
            "category_select": "Technology",
        }
        response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertTrue(form.errors)
        self.flashcard.refresh_from_db()
        self.assertNotEqual(
            self.flashcard.answer, "A subset of AI focused on learning from data."
        )
