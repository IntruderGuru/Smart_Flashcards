# flashcards/tests/test_forms.py
from django.test import TestCase
from unittest.mock import patch
from flashcards.forms import FlashcardForm
from flashcards.services.group_service import GroupService


class FlashcardFormTest(TestCase):
    """
    Testy jednostkowe formularza FlashcardForm.
    """

    @patch.object(
        GroupService, "get_categories", return_value=["Science", "Math", "History"]
    )
    def test_valid_form_with_existing_category(self, mock_get_categories):
        form_data = {
            "question": "What is the boiling point of water?",
            "answer": "100°C",
            "category_select": "Science",
            "category_new": "",
            "source": "Chemistry Textbook",
        }
        form = FlashcardForm(data=form_data)
        self.assertTrue(form.is_valid())
        flashcard = form.save()
        self.assertEqual(flashcard.category, "Science")

    @patch.object(
        GroupService, "get_categories", return_value=["Science", "Math", "History"]
    )
    def test_valid_form_with_new_category(self, mock_get_categories):
        form_data = {
            "question": "What is 2+2?",
            "answer": "4",
            "category_select": "",
            "category_new": "Basic Math",
            "source": "",
        }
        form = FlashcardForm(data=form_data)
        self.assertTrue(form.is_valid())
        flashcard = form.save()
        self.assertEqual(flashcard.category, "Basic Math")

    @patch.object(
        GroupService, "get_categories", return_value=["Science", "Math", "History"]
    )
    def test_invalid_form_no_category(self, mock_get_categories):
        form_data = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "category_select": "",
            "category_new": "",
            "source": "",
        }
        form = FlashcardForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Please select an existing category or enter a new one.",
            form.errors["__all__"],
        )

    @patch.object(
        GroupService, "get_categories", return_value=["Science", "Math", "History"]
    )
    def test_invalid_form_missing_required_fields(self, mock_get_categories):
        form_data = {
            "question": "",
            "answer": "",
            "category_select": "Science",
            "category_new": "",
            "source": "",
        }
        form = FlashcardForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["question"])
        self.assertIn("This field is required.", form.errors["answer"])
