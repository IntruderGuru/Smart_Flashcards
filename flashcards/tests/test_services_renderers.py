# flashcards/tests/test_services_renderers.py
from django.test import TestCase
from unittest.mock import patch, MagicMock, call
from flashcards.services.renderers import TextRenderer, AudioRenderer, RendererFactory
from flashcards.models import Flashcard


class RenderersTest(TestCase):
    """
    Testy jednostkowe dla rendererów Audio i Text.
    """

    def setUp(self):
        self.flashcard = Flashcard.objects.create(
            question="Render Test Q?", answer="Render Test A", category="RenderCat"
        )

    @patch("flashcards.services.renderers.gTTS")
    def test_audio_renderer_success(self, mock_gtts):
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance

        renderer = AudioRenderer()
        audio_data = renderer.render(self.flashcard, language="en")

        mock_gtts.assert_called_with(
            text="Question: Render Test Q?\nAnswer: Render Test A\nCategory: RenderCat\n",
            lang="en",
        )
        mock_tts_instance.write_to_fp.assert_called()
        self.assertIsNotNone(audio_data)

    def test_text_renderer_output(self):
        renderer = TextRenderer()
        rendered = renderer.render(self.flashcard, language="pl")
        expected_output = (
            "--- Flashcard ---\n"
            "Pytanie: Render Test Q?\n"
            "Odpowiedź: Render Test A\n"
            "Kategoria: RenderCat\n"
            "Źródło: \n"
            "-----------------"
        )
        self.assertEqual(rendered, expected_output)

    @patch("flashcards.services.renderers.gTTS")
    def test_audio_renderer_with_invalid_language(self, mock_gtts):
        mock_tts_instance = MagicMock()

        def side_effect(*args, **kwargs):
            if kwargs.get("lang") == "invalid_lang":
                raise ValueError("Invalid language")
            return mock_tts_instance

        mock_gtts.side_effect = side_effect
        renderer = AudioRenderer()
        audio_data = renderer.render(self.flashcard, language="invalid_lang")

        expected_calls = [
            call(
                text="Pytanie: Render Test Q?\nOdpowiedź: Render Test A\nKategoria: RenderCat\n",
                lang="invalid_lang",
            ),
            call(
                text="Question: Render Test Q?\nAnswer: Render Test A\nCategory: RenderCat\n",
                lang="en",
            ),
        ]
        self.assertEqual(mock_gtts.call_args_list, expected_calls)
        self.assertEqual(mock_tts_instance.write_to_fp.call_count, 2)
        self.assertIsNotNone(audio_data)
