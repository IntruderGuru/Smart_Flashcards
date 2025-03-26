# flashcards/tests/test_services_nlp.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from flashcards.services.nlp import NLPProcessor
from flashcards.models import Flashcard
import os


class NLPProcessorTest(TestCase):
    """
    Testy przetwarzania tekstu przy użyciu OpenAI (mock) w NLPProcessor.
    """

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch("flashcards.services.nlp.openai.chat.completions.create")
    def test_generate_flashcards_from_text_mocked(self, mock_openai_create):
        mock_message = MagicMock()
        mock_message.content = (
            "question: What is Python?\nanswer: A programming language\n---"
        )

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_openai_create.return_value = mock_response

        nlp = NLPProcessor()
        flashcards = nlp.analyze_text("Some text about Python.", "Programming")
        self.assertEqual(len(flashcards), 1)
        self.assertEqual(flashcards[0].question, "What is Python?")
        self.assertEqual(flashcards[0].answer, "A programming language")
        self.assertEqual(flashcards[0].category, "Programming")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch(
        "flashcards.services.nlp.openai.chat.completions.create",
        side_effect=Exception("API Error"),
    )
    def test_analyze_text_api_error(self, mock_openai_create):
        nlp = NLPProcessor()
        with self.assertRaises(RuntimeError) as context:
            nlp.analyze_text("Some text", "Biology")
        self.assertIn("Error generating flashcards: API Error", str(context.exception))

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch("flashcards.services.nlp.openai.chat.completions.create")
    def test_analyze_text_success(self, mock_openai_create):
        mock_message = MagicMock()
        mock_message.content = (
            "question: What is AI?\nanswer: Artificial Intelligence\n---"
        )
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai_create.return_value = mock_response

        nlp = NLPProcessor()
        flashcards = nlp.analyze_text("Explain AI.", "Technology")
        self.assertEqual(len(flashcards), 1)
        self.assertEqual(flashcards[0].question, "What is AI?")
        self.assertEqual(flashcards[0].answer, "Artificial Intelligence")
        self.assertEqual(flashcards[0].category, "Technology")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch("flashcards.services.nlp.openai.chat.completions.create")
    def test_generate_flashcards_from_text_with_multiple_flashcards(
        self, mock_openai_create
    ):
        mock_message = MagicMock()
        mock_message.content = (
            "question: What is Python?\nanswer: A programming language.\n---\n"
            "question: What is Django?\nanswer: A Python web framework.\n---"
        )
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai_create.return_value = mock_response

        nlp = NLPProcessor()
        flashcards = nlp.analyze_text("Explain Python and Django.", "Programming")

        self.assertEqual(len(flashcards), 2)
        self.assertEqual(flashcards[0].question, "What is Python?")
        self.assertEqual(flashcards[1].question, "What is Django?")
