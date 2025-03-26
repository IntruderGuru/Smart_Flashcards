# flashcards/tests/test_views_learn.py
from django.test import TestCase
from django.urls import reverse
from flashcards.models import Flashcard


class LearnFlashcardsViewTest(TestCase):
    """
    Testy widoku LearnFlashcardsView: wybór kolejnych fiszek i aktualizacja statystyk.
    """

    def setUp(self):
        self.category = "Technology"
        self.flashcard1 = Flashcard.objects.create(
            question="What is AI?",
            answer="Artificial Intelligence.",
            category=self.category,
        )
        self.flashcard2 = Flashcard.objects.create(
            question="What is ML?",
            answer="Machine Learning.",
            category=self.category,
        )
        self.learn_url = reverse(
            "flashcards:learn_flashcards", kwargs={"category": self.category}
        )

    def test_learn_flashcards_view_get(self):
        response = self.client.get(self.learn_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/learn_flashcard.html")
        self.assertIn("flashcard", response.context)
        self.assertFalse(response.context["show_answer"])

    def test_learn_flashcards_view_post_show_answer(self):
        self.client.get(self.learn_url)  # Inicjalizacja
        response = self.client.post(
            self.learn_url, {"flashcard_id": self.flashcard1.pk, "show_answer": "on"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.flashcard1.answer)
        self.assertTrue(response.context["show_answer"])

    def test_learn_flashcards_view_post_correct_answer(self):
        self.client.get(self.learn_url)
        response = self.client.post(
            self.learn_url, {"flashcard_id": self.flashcard1.pk, "correct": "on"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.learn_url)
        self.flashcard1.refresh_from_db()
        self.assertEqual(self.flashcard1.correct_answers, 1)

    def test_learn_flashcards_view_post_incorrect_answer(self):
        self.client.get(self.learn_url)
        response = self.client.post(
            self.learn_url, {"flashcard_id": self.flashcard2.pk, "incorrect": "on"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.learn_url)
        self.flashcard2.refresh_from_db()
        self.assertEqual(self.flashcard2.incorrect_answers, 1)
