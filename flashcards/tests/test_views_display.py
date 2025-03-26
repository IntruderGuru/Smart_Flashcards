# flashcards/tests/test_views_display.py
from django.test import TestCase
from django.urls import reverse
from flashcards.models import Flashcard


class DisplayFlashcardViewTest(TestCase):
    """
    Testy wyświetlania pojedynczej fiszki w formacie tekstowym lub audio.
    """

    def setUp(self):
        self.flashcard = Flashcard.objects.create(
            question="What is REST?",
            answer="Representational State Transfer.",
            category="Technology",
        )
        self.display_url = reverse(
            "flashcards:display_flashcard", kwargs={"pk": self.flashcard.pk}
        )

    def test_display_flashcard_view_text_format(self):
        response = self.client.get(self.display_url, {"format": "text", "lang": "en"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/display_flashcard.html")
        self.assertContains(response, "What is REST?")
        self.assertContains(response, "Representational State Transfer.")

    def test_display_flashcard_view_audio_format(self):
        response = self.client.get(self.display_url, {"format": "audio", "lang": "en"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/display_flashcard.html")
        expected_audio_src = f"/audio/{self.flashcard.pk}/en/"
        self.assertContains(response, f'src="{expected_audio_src}"')
        self.assertContains(response, "<audio")
        self.assertContains(response, "What is REST?")

    def test_display_flashcard_view_default_format(self):
        response = self.client.get(self.display_url, {"lang": "en"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/display_flashcard.html")
        self.assertContains(response, "What is REST?")
        self.assertContains(response, "Representational State Transfer.")
        self.assertNotContains(response, "<audio")

    def test_display_flashcard_view_invalid_format(self):
        response = self.client.get(self.display_url, {"format": "video", "lang": "en"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/display_flashcard.html")
        self.assertContains(response, "What is REST?")
