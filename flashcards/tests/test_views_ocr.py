# flashcards/tests/test_views_ocr.py
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from django.contrib.messages import get_messages
from flashcards.models import Flashcard


class OCRResultsViewTest(TestCase):
    """
    Testy widoku przetwarzającego obraz do fiszek (OCRResultsView).
    """

    def setUp(self):
        self.ocr_url = reverse("flashcards:ocr_results")
        self.category = "Science"

    @patch(
        "flashcards.views.flashcards_views.FlashcardFacade.generate_flashcards_from_image"
    )
    def test_ocr_results_view_post_valid_image(self, mock_generate_flashcards):
        image = SimpleUploadedFile(
            "test_image.png", b"file_content", content_type="image/png"
        )

        mock_flashcard1 = MagicMock(spec=Flashcard)
        mock_flashcard1.question = "What is the boiling point of water?"
        mock_flashcard1.answer = "100°C"
        mock_flashcard1.category = self.category

        mock_flashcard2 = MagicMock(spec=Flashcard)
        mock_flashcard2.question = "What is the chemical formula of water?"
        mock_flashcard2.answer = "H₂O"
        mock_flashcard2.category = self.category

        mock_generate_flashcards.return_value = [mock_flashcard1, mock_flashcard2]

        response = self.client.post(
            self.ocr_url, {"image": image, "category": self.category}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/ocr_results.html")
        self.assertEqual(len(response.context["flashcards"]), 2)
        session_flashcards = self.client.session.get("temp_flashcards")
        self.assertIsNotNone(session_flashcards)
        self.assertEqual(len(session_flashcards), 2)

    def test_ocr_results_view_post_no_image(self):
        response = self.client.post(
            self.ocr_url, {"category": self.category}, follow=True
        )
        self.assertRedirects(response, reverse("flashcards:upload_photo"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "No image file provided.")

    @patch(
        "flashcards.views.flashcards_views.FlashcardFacade.generate_flashcards_from_image",
        side_effect=Exception("OCR Failure"),
    )
    def test_ocr_results_view_post_exception(self, mock_generate_flashcards):
        image = SimpleUploadedFile(
            "test_image.png", b"file_content", content_type="image/png"
        )

        response = self.client.post(
            self.ocr_url, {"image": image, "category": self.category}, follow=True
        )
        self.assertRedirects(response, reverse("flashcards:upload_photo"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "An error occurred during OCR processing. Please try again.",
        )
