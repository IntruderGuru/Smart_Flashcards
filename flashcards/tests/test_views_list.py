# flashcards/tests/test_views_list.py
from django.test import TestCase
from django.urls import reverse
from flashcards.models import Flashcard


class FlashcardListViewAdditionalTest(TestCase):
    """
    Testy rozszerzone widoku listy fiszek (FlashcardListView), w tym paginacji.
    """

    def setUp(self):
        self.list_url = reverse("flashcards:flashcard_list")
        for i in range(12):
            category = f"Category_{i}"
            for j in range(5):
                Flashcard.objects.create(
                    question=f"Question {i}-{j}",
                    answer=f"Answer {i}-{j}",
                    category=category,
                )

    def test_flashcard_list_view_pagination_categories(self):
        response = self.client.get(self.list_url, {"page_categories": 1})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/flashcard_list.html")
        self.assertEqual(len(response.context["page_obj_categories"]), 5)

        response = self.client.get(self.list_url, {"page_categories": 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj_categories"]), 2)

    def test_flashcard_list_view_flashcards_pagination(self):
        response = self.client.get(
            self.list_url, {"page_categories": 1, "page_flashcards_Category_0": 2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("flashcards_by_category", response.context)
        self.assertEqual(
            len(response.context["flashcards_by_category"]["Category_0"]), 5
        )

    def test_flashcard_list_view_no_flashcards(self):
        Flashcard.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["flashcards_by_category"]), 0)

    def test_flashcard_list_view_with_flashcards(self):
        Flashcard.objects.all().delete()

        Flashcard.objects.create(question="Q1", answer="A1", category="Science")
        Flashcard.objects.create(question="Q2", answer="A2", category="Math")
        Flashcard.objects.create(question="Q3", answer="A3", category="Science")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/flashcard_list.html")

        self.assertEqual(len(response.context["flashcards_by_category"]), 2)
        self.assertEqual(len(response.context["flashcards_by_category"]["Science"]), 2)
        self.assertEqual(len(response.context["flashcards_by_category"]["Math"]), 1)
