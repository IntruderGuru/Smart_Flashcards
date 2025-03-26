# flashcards/tests/test_views_upload_photo.py
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from django.contrib.messages import get_messages
from flashcards.models import Flashcard


class UploadPhotoViewTest(TestCase):
    """
    Testy widoku wgrywania zdjęcia (UploadPhotoView).
    """

    def setUp(self):
        self.upload_url = reverse("flashcards:upload_photo")

    @patch(
        "flashcards.views.flashcards_views.FlashcardFacade.generate_flashcards_from_image"
    )
    def test_upload_photo_view_post_valid_image(self, mock_generate_flashcards):
        image = SimpleUploadedFile(
            "test_image.png", b"file_content", content_type="image/png"
        )

        mock_flashcard1 = MagicMock(spec=Flashcard)
        mock_flashcard1.question = "What is HTML?"
        mock_flashcard1.answer = "HyperText Markup Language."
        mock_flashcard1.category = "Web Development"

        mock_flashcard2 = MagicMock(spec=Flashcard)
        mock_flashcard2.question = "What does CSS stand for?"
        mock_flashcard2.answer = "Cascading Style Sheets."
        mock_flashcard2.category = "Web Development"

        mock_generate_flashcards.return_value = [mock_flashcard1, mock_flashcard2]

        response = self.client.post(self.upload_url, {"photo": image}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/ocr_results.html")
        self.assertEqual(len(response.context["flashcards"]), 2)
        session_flashcards = self.client.session.get("temp_flashcards")
        self.assertEqual(len(session_flashcards), 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Successfully generated 2 flashcards.")

    def test_upload_photo_view_post_no_file(self):
        response = self.client.post(self.upload_url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/upload_photo.html")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "No image file provided.")

    @patch(
        "flashcards.views.flashcards_views.FlashcardFacade.generate_flashcards_from_image",
        side_effect=Exception("Processing Failure"),
    )
    def test_upload_photo_view_post_exception(self, mock_generate_flashcards):
        image = SimpleUploadedFile(
            "test_image.png", b"file_content", content_type="image/png"
        )
        response = self.client.post(self.upload_url, {"photo": image}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/upload_photo.html")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), "An error occurred while processing the image."
        )

    def test_upload_photo_view_post_invalid_file_type(self):
        non_image = SimpleUploadedFile(
            "test_document.txt", b"file_content", content_type="text/plain"
        )
        response = self.client.post(self.upload_url, {"photo": non_image}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/upload_photo.html")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "The uploaded file is not an image.")
