# flashcards/tests/test_urls.py
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from flashcards.views.flashcards_views import (
    FlashcardListView,
    AddFlashcardView,
    EditFlashcardView,
    DeleteFlashcardView,
    DisplayFlashcardView,
    FlashcardAudioView,
    LearnFlashcardsView,
    OCRResultsView,
    SaveFlashcardsView,
    GenerateFromTextView,
    UploadPhotoView,
)


class FlashcardsURLTest(SimpleTestCase):
    """
    Testy czarnoskrzynkowe: sprawdzają, czy adresy URL rozpoznawane są przez właściwe klasy widoków.
    """

    def test_flashcard_list_url_resolves(self):
        url = reverse("flashcards:flashcard_list")
        self.assertEqual(resolve(url).func.view_class, FlashcardListView)

    def test_add_flashcard_url_resolves(self):
        url = reverse("flashcards:add_flashcard")
        self.assertEqual(resolve(url).func.view_class, AddFlashcardView)

    def test_edit_flashcard_url_resolves(self):
        url = reverse("flashcards:edit_flashcard", args=[1])
        self.assertEqual(resolve(url).func.view_class, EditFlashcardView)

    def test_delete_flashcard_url_resolves(self):
        url = reverse("flashcards:delete_flashcard", args=[1])
        self.assertEqual(resolve(url).func.view_class, DeleteFlashcardView)

    def test_display_flashcard_url_resolves(self):
        url = reverse("flashcards:display_flashcard", args=[1])
        self.assertEqual(resolve(url).func.view_class, DisplayFlashcardView)

    def test_flashcard_audio_url_resolves(self):
        url = reverse("flashcards:flashcard_audio", args=[1, "en"])
        self.assertEqual(resolve(url).func.view_class, FlashcardAudioView)

    def test_learn_flashcards_url_resolves(self):
        url = reverse("flashcards:learn_flashcards", args=["Science"])
        self.assertEqual(resolve(url).func.view_class, LearnFlashcardsView)

    def test_ocr_results_url_resolves(self):
        url = reverse("flashcards:ocr_results")
        self.assertEqual(resolve(url).func.view_class, OCRResultsView)

    def test_save_flashcards_url_resolves(self):
        url = reverse("flashcards:save_flashcards")
        self.assertEqual(resolve(url).func.view_class, SaveFlashcardsView)

    def test_generate_from_text_url_resolves(self):
        url = reverse("flashcards:generate_from_text")
        self.assertEqual(resolve(url).func.view_class, GenerateFromTextView)

    def test_upload_photo_url_resolves(self):
        url = reverse("flashcards:upload_photo")
        self.assertEqual(resolve(url).func.view_class, UploadPhotoView)
