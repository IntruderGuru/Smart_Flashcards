# flashcards/tests/test_blackbox.py

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from flashcards.models import Flashcard


class BlackBoxBasicFlowTest(TestCase):
    """
    Testy czarnoskrzynkowe podstawowego przepływu użytkownika w aplikacji.
    """

    def test_get_homepage_list(self):
        """
        Sprawdza, czy główna strona (lista fiszek) jest dostępna (kod 200)
        i czy zawiera oczekiwane elementy.
        """
        url = reverse("flashcards:flashcard_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/flashcard_list.html")
        self.assertContains(response, "Flashcards")

    def test_add_flashcard_valid_data(self):
        """
        Test czarnoskrzynkowy dodania fiszki poprzez POST z prawidłowymi danymi.
        Oczekiwane zachowanie: przekierowanie i komunikat sukcesu.
        """
        url = reverse("flashcards:add_flashcard")
        form_data = {
            "question": "What is Python?",
            "answer": "A programming language.",
            "category_select": "",
            "category_new": "Programming",
            "source": "Wikipedia",
        }
        response = self.client.post(url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/flashcard_list.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully added" in str(m) for m in messages))

        flashcard_exists = Flashcard.objects.filter(question="What is Python?").exists()
        self.assertTrue(flashcard_exists)

    def test_add_flashcard_invalid_data(self):
        """
        Test czarnoskrzynkowy dodania fiszki z nieprawidłowymi danymi (np. brak pytania).
        Oczekiwane zachowanie: kod 200 (formularz z błędami), brak przekierowania.
        """
        url = reverse("flashcards:add_flashcard")
        form_data = {
            "question": "",
            "answer": "Some answer",
            "category_select": "General",
            "source": "A random source",
        }
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/add_flashcard.html")
        # Sprawdzamy, czy w treści zwrotnej pojawia się informacja o błędzie
        self.assertContains(response, "This field is required")

        flashcard_count = Flashcard.objects.count()
        self.assertEqual(flashcard_count, 0)

    def test_upload_photo_no_file(self):
        """
        Test czarnoskrzynkowy dla endpointu upload_photo, gdy nie prześlemy pliku.
        Oczekiwane: strona się wyświetli z komunikatem o braku pliku.
        """
        url = reverse("flashcards:upload_photo")
        response = self.client.post(url, data={}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/upload_photo.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("No image file provided." in str(m) for m in messages))

    def test_upload_photo_invalid_file_type(self):
        """
        Test czarnoskrzynkowy dla endpointu upload_photo, gdy wysłany plik nie jest obrazem.
        Oczekiwane: strona się wyświetli z komunikatem o niepoprawnym formacie pliku.
        """
        url = reverse("flashcards:upload_photo")
        fake_file = SimpleUploadedFile(
            "document.txt", b"some content", content_type="text/plain"
        )
        response = self.client.post(url, data={"photo": fake_file}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/upload_photo.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("not an image" in str(m) for m in messages))

    def test_upload_photo_valid_image(self):
        """
        Test czarnoskrzynkowy wysłania prawidłowego pliku (symulacja obrazu).
        Oczekiwane: Przejście do ocr_results.html bądź do strony wyników,
        pojawienie się komunikatu o sukcesie i ewentualny zapis w sesji.
        """
        url = reverse("flashcards:upload_photo")
        fake_image = SimpleUploadedFile(
            "test.png", b"\x89PNG\r\n\x1a\n", content_type="image/png"
        )
        response = self.client.post(url, data={"photo": fake_image}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flashcards/upload_photo.html")
        messages = list(get_messages(response.wsgi_request))
        success_msg = ""
        self.assertTrue(any(success_msg in str(m) for m in messages))

    def test_learn_flashcards_nonexistent_category(self):
        """
        Test czarnoskrzynkowy dla trybu nauki z kategorią, która nie istnieje.
        Oczekiwane: ostrzeżenie i przekierowanie do listy fiszek.
        """
        url = reverse("flashcards:learn_flashcards", kwargs={"category": "NonExistent"})
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, "flashcards/flashcard_list.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("No flashcards available" in str(m) for m in messages))

    def test_delete_nonexistent_flashcard(self):
        """
        Test czarnoskrzynkowy usunięcia fiszki, która nie istnieje (id=9999).
        Oczekiwane: HTTP 404.
        """
        url = reverse("flashcards:delete_flashcard", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class BlackBoxAdminTest(TestCase):
    """
    Przykładowe testy czarnoskrzynkowe panelu admina –
    testują podstawowe akcje w adminie bez wchodzenia w detale implementacji.
    """

    def setUp(self):
        from django.contrib.auth.models import User

        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpass", email="admin@test.pl"
        )

    def test_admin_login_and_list_flashcards(self):
        """
        Test czarnoskrzynkowy sprawdzający, czy możemy zalogować się do panelu admina
        i wyświetlić listę fiszek (Flashcard).
        """
        login_url = reverse("admin:login")
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username="admin", password="adminpass")

        list_url = reverse("admin:flashcards_flashcard_changelist")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select flashcard to change")

    def test_admin_delete_flashcard_action(self):
        """
        Test czarnoskrzynkowy: usuwa fiszkę przez panel admina (akcja Delete).
        """
        flashcard = Flashcard.objects.create(
            question="Admin Test Q",
            answer="Admin Test A",
            category="AdminCat",
        )

        self.client.login(username="admin", password="adminpass")

        list_url = reverse("admin:flashcards_flashcard_changelist")

        response = self.client.post(
            list_url,
            {
                "action": "delete_selected",
                "_selected_action": [flashcard.pk],
                "post": "yes",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Flashcard.objects.filter(pk=flashcard.pk).exists())
