# flashcards/tests/test_views_delete.py
from django.test import TestCase
from django.urls import reverse
from flashcards.models import Flashcard


class DeleteFlashcardViewTest(TestCase):
    """
    Testy widoku usuwania fiszki (DeleteFlashcardView).
    """

    def setUp(self):
        self.flashcard = Flashcard.objects.create(
            question="What is HTTP?",
            answer="HyperText Transfer Protocol.",
            category="Technology",
        )
        self.delete_url = reverse(
            "flashcards:delete_flashcard", kwargs={"pk": self.flashcard.pk}
        )

    def test_delete_flashcard_view_get(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/confirm_delete.html")
        self.assertContains(response, "Are you sure you want to delete")

    def test_delete_flashcard_view_post(self):
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("flashcards:flashcard_list"))
        self.assertFalse(Flashcard.objects.filter(pk=self.flashcard.pk).exists())
