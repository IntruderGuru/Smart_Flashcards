# flashcards/tests/test_views_flashcard_audio.py
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from flashcards.models import Flashcard


class FlashcardAudioViewTest(TestCase):
    """
    Testy widoku FlashcardAudioView: generowanie danych audio dla fiszki.
    """

    def setUp(self):
        self.flashcard = Flashcard.objects.create(
            question="What is JSON?",
            answer="JavaScript Object Notation.",
            category="Technology",
        )
        self.audio_url_en = reverse(
            "flashcards:flashcard_audio", kwargs={"pk": self.flashcard.pk, "lang": "en"}
        )
        self.audio_url_invalid = reverse(
            "flashcards:flashcard_audio",
            kwargs={"pk": self.flashcard.pk, "lang": "invalid_lang"},
        )
        self.audio_url_nonexistent = reverse(
            "flashcards:flashcard_audio", kwargs={"pk": 999, "lang": "en"}
        )

    @patch("flashcards.views.flashcards_views.RendererFactory.get_renderer")
    def test_flashcard_audio_view_invalid_language_fallback(self, mock_get_renderer):
        mock_audio_renderer = MagicMock()
        mock_audio_renderer.render.side_effect = [
            ValueError("Invalid language"),
            b"Fallback audio data",
        ]
        mock_get_renderer.return_value = mock_audio_renderer

        response = self.client.get(self.audio_url_invalid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Fallback audio data")
        self.assertEqual(response["Content-Type"], "audio/mpeg")

    @patch("flashcards.views.flashcards_views.RendererFactory.get_renderer")
    def test_flashcard_audio_view_valid_language(self, mock_get_renderer):
        mock_audio_renderer_en = MagicMock()
        mock_audio_renderer_en.render.return_value = b"Valid audio data"
        mock_get_renderer.return_value = mock_audio_renderer_en

        response = self.client.get(self.audio_url_en)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Valid audio data")
        self.assertEqual(response["Content-Type"], "audio/mpeg")
        mock_audio_renderer_en.render.assert_called_once_with(
            self.flashcard, language="en"
        )

    def test_flashcard_audio_view_nonexistent_flashcard(self):
        response = self.client.get(self.audio_url_nonexistent)
        self.assertEqual(response.status_code, 404)
