from django.urls import path
from .views.flashcards_views import (
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

app_name = "flashcards"
urlpatterns = [
    path("", FlashcardListView.as_view(), name="flashcard_list"),
    path("add/", AddFlashcardView.as_view(), name="add_flashcard"),
    path("edit/<int:pk>/", EditFlashcardView.as_view(), name="edit_flashcard"),
    path("delete/<int:pk>/", DeleteFlashcardView.as_view(), name="delete_flashcard"),
    path("display/<int:pk>/", DisplayFlashcardView.as_view(), name="display_flashcard"),
    path(
        "audio/<int:pk>/<str:lang>/",
        FlashcardAudioView.as_view(),
        name="flashcard_audio",
    ),
    path(
        "learn/<str:category>/", LearnFlashcardsView.as_view(), name="learn_flashcards"
    ),
    path("ocr/results/", OCRResultsView.as_view(), name="ocr_results"),
    path("save_flashcards/", SaveFlashcardsView.as_view(), name="save_flashcards"),
    path(
        "generate_from_text/", GenerateFromTextView.as_view(), name="generate_from_text"
    ),
    path("upload_photo/", UploadPhotoView.as_view(), name="upload_photo"),
]
