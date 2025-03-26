# flashcards/tests/test_decorators.py
from django.test import TestCase, RequestFactory
from unittest.mock import patch
from django.contrib.auth.models import User
from flashcards.decorators import log_flashcard_action
from flashcards.models import Flashcard


class MockAdminModelAdmin:
    """
    Mock administracyjny, pozwalający symulować metodę delete_model.
    """

    def delete_model(self, request, obj):
        obj.delete()


class FlashcardDecoratorTest(TestCase):
    """
    Testy jednostkowe dekoratora log_flashcard_action.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.flashcard = Flashcard.objects.create(
            question="Test Question?", answer="Test Answer", category="TestCat"
        )
        self.admin = MockAdminModelAdmin()

    @patch("flashcards.decorators.logger")
    def test_log_flashcard_action_decorator(self, mock_logger):
        """
        Sprawdza, czy dekorator poprawnie loguje rozpoczęcie i zakończenie akcji.
        """
        request = self.factory.post("/admin/delete/")
        request.user = self.user

        decorated_delete = log_flashcard_action("Delete flashcard")(
            self.admin.delete_model
        )
        decorated_delete(request, self.flashcard)

        mock_logger.info.assert_any_call("Started action: Delete flashcard")
        mock_logger.info.assert_any_call("Finished action: Delete flashcard")
