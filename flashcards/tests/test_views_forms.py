# flashcards/tests/test_views_forms.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest.mock import patch
from flashcards.models import Flashcard


class FlashcardViewFormTest(TestCase):
    """
    Testy integracyjne widoku i formularza dodawania fiszek.
    """

    def setUp(self):
        self.add_url = reverse("flashcards:add_flashcard")
        self.list_url = reverse("flashcards:flashcard_list")

    def test_add_flashcard_view_get(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/add_flashcard.html")

    @patch(
        "flashcards.services.group_service.GroupService.get_categories",
        return_value=["Science", "Math"],
    )
    def test_post_add_flashcard_with_existing_category(self, mock_get_categories):
        form_data = {
            "question": "What is the speed of light?",
            "answer": "Approximately 299,792 km per second.",
            "category_select": "Science",
            "category_new": "",
            "source": "Physics Textbook",
        }
        response = self.client.post(self.add_url, data=form_data, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertTrue(
            Flashcard.objects.filter(question="What is the speed of light?").exists()
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Flashcard has been successfully added.")

    @patch(
        "flashcards.services.group_service.GroupService.get_categories",
        return_value=["Science", "Math"],
    )
    def test_post_add_flashcard_with_new_category(self, mock_get_categories):
        form_data = {
            "question": "What is the integral of x dx?",
            "answer": "0.5x^2 + C",
            "category_select": "",
            "category_new": "Calculus",
            "source": "",
        }
        response = self.client.post(self.add_url, data=form_data, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertTrue(
            Flashcard.objects.filter(question="What is the integral of x dx?").exists()
        )
        flashcard = Flashcard.objects.get(question="What is the integral of x dx?")
        self.assertEqual(flashcard.category, "Calculus")

    @patch(
        "flashcards.services.group_service.GroupService.get_categories",
        return_value=["Science", "Math"],
    )
    def test_post_add_flashcard_invalid_form(self, mock_get_categories):
        form_data = {
            "question": "",
            "answer": "",
            "category_select": "",
            "category_new": "",
            "source": "",
        }
        response = self.client.post(self.add_url, data=form_data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get("form", None)
        self.assertTrue(form.errors)
        self.assertFalse(Flashcard.objects.exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
