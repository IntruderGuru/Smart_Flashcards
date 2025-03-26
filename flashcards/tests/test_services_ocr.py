# flashcards/tests/test_services_ocr.py

from django.test import TestCase
from unittest.mock import patch, MagicMock
from flashcards.services.ocr import OCRProcessor
from flashcards.models import Flashcard
from django.db import IntegrityError


class OCRProcessorTest(TestCase):
    """
    Testy usługi OCRProcessor: ekstrakcja tekstu, generowanie fiszek i obsługa błędów.
    """

    @patch("flashcards.services.ocr.pytesseract.image_to_string")
    def test_extract_text_success(self, mock_pytesseract):
        mock_pytesseract.return_value = (
            "I am having trouble getting my Discord chatbot to send a query to OpenAI to generate a response. "
            "The OpenAI API key always shows a status of never being used, even though the query is supposed to be "
            "sent using this key, but it's not happening. Simply, the OpenAI API key wouldn't be used in the query. "
            "I tried using global variables and it didn't work, adding attributes to functions with the API key also "
            "didn't work, updating the OpenAI library in Python, following error instructions but fixing one error led "
            "to another, searching for information on this topic on the internet, and now seeking help here"
        )

        text = OCRProcessor.extract_text(
            "C:/Users/barte/fiszki_app/documents/image2.png"
        )
        self.assertEqual(
            text,
            "I am having trouble getting my Discord chatbot to send a query to OpenAI to generate a response. "
            "The OpenAI API key always shows a status of never being used, even though the query is supposed to be "
            "sent using this key, but it's not happening. Simply, the OpenAI API key wouldn't be used in the query. "
            "I tried using global variables and it didn't work, adding attributes to functions with the API key also "
            "didn't work, updating the OpenAI library in Python, following error instructions but fixing one error led "
            "to another, searching for information on this topic on the internet, and now seeking help here",
        )

    @patch(
        "flashcards.services.ocr.pytesseract.image_to_string",
        side_effect=FileNotFoundError,
    )
    def test_extract_text_file_not_found(self, mock_pytesseract):
        text = OCRProcessor.extract_text("path/to/nonexistent_image.png")
        self.assertEqual(text, "")

    @patch(
        "flashcards.services.ocr.pytesseract.image_to_string",
        side_effect=Exception("OCR error while processing image"),
    )
    def test_extract_text_exception(self, mock_pytesseract):
        text = OCRProcessor.extract_text(
            "C:/Users/barte/fiszki_app/documents/image3.png"
        )
        self.assertEqual(text, "")

    @patch("flashcards.services.ocr.OCRProcessor.analyze_text_and_generate_flashcards")
    def test_analyze_text_and_generate_flashcards(self, mock_analyze):
        mock_flashcard1 = MagicMock(spec=Flashcard)
        mock_flashcard2 = MagicMock(spec=Flashcard)
        mock_analyze.return_value = [mock_flashcard1, mock_flashcard2]

        flashcards = OCRProcessor.analyze_text_and_generate_flashcards(
            "Some text", "OCRCat"
        )
        self.assertEqual(len(flashcards), 2)

    @patch(
        "flashcards.services.ocr.OCRProcessor.analyze_text_and_generate_flashcards",
        side_effect=Exception("DB Error"),
    )
    def test_analyze_text_and_generate_flashcards_db_error(self, mock_analyze):
        with self.assertRaises(Exception) as context:
            OCRProcessor.analyze_text_and_generate_flashcards("Some text", "OCRCat")
        self.assertIn("DB Error", str(context.exception))

    def test_analyze_text_and_generate_flashcards_empty_text(self):
        flashcards = OCRProcessor.analyze_text_and_generate_flashcards("", "General")
        self.assertEqual(len(flashcards), 0)

    def test_analyze_text_and_generate_flashcards_no_questions(self):
        text = "This is a text without questions."
        flashcards = OCRProcessor.analyze_text_and_generate_flashcards(text, "General")
        self.assertEqual(len(flashcards), 0)

    @patch("flashcards.services.ocr.Flashcard.objects.bulk_create")
    def test_analyze_text_and_generate_flashcards_success(self, mock_bulk_create):
        text = "QUESTION1\nAnswer1\nQUESTION2\nAnswer2"
        flashcards = OCRProcessor.analyze_text_and_generate_flashcards(
            text, "Programming"
        )
        self.assertEqual(len(flashcards), 2)
        mock_bulk_create.assert_called_once_with(flashcards)

    @patch.object(
        Flashcard.objects, "bulk_create", side_effect=IntegrityError("DB Error")
    )
    def test_analyze_text_and_generate_flashcards_bulk_create_integrity_error(
        self, mock_bulk_create
    ):
        text = "QUESTION1\nAnswer1\nQUESTION2\nAnswer2"
        with self.assertLogs("flashcards.services.ocr", level="ERROR") as log:
            flashcards = OCRProcessor.analyze_text_and_generate_flashcards(
                text, "Programming"
            )
        self.assertEqual(len(flashcards), 2)
        self.assertIn(
            "ERROR:flashcards.services.ocr:Database error while saving flashcards: DB Error",
            log.output,
        )
