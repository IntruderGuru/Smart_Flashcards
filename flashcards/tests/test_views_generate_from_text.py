# flashcards/tests/test_views_generate_from_text.py

from django.test import TestCase
from django.urls import reverse
from flashcards.models import Flashcard
from unittest.mock import patch, MagicMock
from django.contrib.messages import get_messages


class GenerateFromTextViewTest(TestCase):
    """
    Testy widoku generowania fiszek z tekstu.
    """

    def setUp(self):
        self.generate_url = reverse("flashcards:generate_from_text")
        self.category = "Mathematics"

    @patch(
        "flashcards.views.flashcards_views.FlashcardFacade.generate_flashcards_from_text"
    )
    def test_generate_from_text_view_post_valid_text(self, mock_generate_flashcards):
        mock_flashcard1 = MagicMock(spec=Flashcard)
        mock_flashcard1.question = "What is 2+2?"
        mock_flashcard1.answer = "4"
        mock_flashcard1.category = self.category

        mock_flashcard2 = MagicMock(spec=Flashcard)
        mock_flashcard2.question = "What is the derivative of x²?"
        mock_flashcard2.answer = "2x"
        mock_flashcard2.category = self.category

        mock_generate_flashcards.return_value = [mock_flashcard1, mock_flashcard2]

        text_input = "Some mathematical concepts."
        response = self.client.post(
            self.generate_url, {"text": text_input}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/generate_from_text.html")
        self.assertIn("flashcards", response.context)
        self.assertEqual(len(response.context["flashcards"]), 2)
        self.assertEqual(response.context["flashcards"][0]["answer"], "4")

        session_flashcards = self.client.session.get("temp_flashcards")
        self.assertIsNotNone(session_flashcards)
        self.assertEqual(len(session_flashcards), 2)
        self.assertEqual(
            session_flashcards[1]["question"], "What is the derivative of x²?"
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Successfully generated 2 flashcards from the provided text.",
        )

    def test_generate_from_text_view_post_empty_text(self):
        response = self.client.post(self.generate_url, {"text": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/generate_from_text.html")
        self.assertIn("flashcards", response.context)
        self.assertEqual(len(response.context["flashcards"]), 0)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The text field cannot be empty.")

    @patch(
        "flashcards.views.flashcards_views.FlashcardFacade.generate_flashcards_from_text",
        side_effect=Exception("NLP Failure"),
    )
    def test_generate_from_text_view_post_exception(self, mock_generate_flashcards):
        text_input = "Some text that causes an exception."
        response = self.client.post(
            self.generate_url, {"text": text_input}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/generate_from_text.html")
        self.assertIn("flashcards", response.context)
        self.assertEqual(len(response.context["flashcards"]), 0)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "An error occurred while generating flashcards."
        )
