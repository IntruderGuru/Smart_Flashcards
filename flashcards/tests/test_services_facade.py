# flashcards/tests/test_services_facade.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from flashcards.services.flashcard_facade import FlashcardFacade
from flashcards.models import Flashcard


class FlashcardFacadeTest(TestCase):
    """
    Testy integrujące komponenty OCR i NLP przez warstwę FlashcardFacade.
    """

    @patch("flashcards.services.flashcard_facade.OCRProcessor.extract_text")
    @patch("flashcards.services.flashcard_facade.NLPProcessor.analyze_text")
    def test_generate_flashcards_from_image(self, mock_analyze_text, mock_extract_text):
        mock_extract_text.return_value = "Sample extracted text."

        mock_flashcard1 = MagicMock(spec=Flashcard)
        mock_flashcard1.question = "What is sample?"
        mock_flashcard1.answer = "This is a sample."
        mock_flashcard1.category = "SampleCat"

        mock_flashcard2 = MagicMock(spec=Flashcard)
        mock_flashcard2.question = "Another question?"
        mock_flashcard2.answer = "Another answer."
        mock_flashcard2.category = "SampleCat"

        mock_analyze_text.return_value = [mock_flashcard1, mock_flashcard2]

        flashcards = FlashcardFacade.generate_flashcards_from_image(
            "C:/Users/barte/fiszki_app/documents/image.png", "SampleCat"
        )
        self.assertEqual(len(flashcards), 2)
        self.assertEqual(flashcards[0].category, "SampleCat")
        self.assertEqual(flashcards[1].category, "SampleCat")

    @patch("flashcards.services.flashcard_facade.OCRProcessor.extract_text")
    @patch("flashcards.services.flashcard_facade.NLPProcessor.analyze_text")
    def test_generate_flashcards_from_empty_image(self, mock_analyze, mock_extract):
        mock_extract.return_value = ""
        with self.assertRaises(ValueError):
            FlashcardFacade.generate_flashcards_from_image(
                "C:/Users/barte/fiszki_app/documents/image3.png"
            )

    @patch("flashcards.services.flashcard_facade.OCRProcessor.extract_text")
    def test_generate_flashcards_from_image_file_not_found(self, mock_extract_text):
        mock_extract_text.return_value = ""
        with self.assertRaises(ValueError) as context:
            FlashcardFacade.generate_flashcards_from_image(
                "path/to/nonexistent_image.png"
            )
        self.assertEqual(
            str(context.exception), "Failed to extract text from the image."
        )
