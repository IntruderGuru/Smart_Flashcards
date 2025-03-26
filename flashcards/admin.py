from django.contrib import admin
from .models import Flashcard
from .decorators import log_flashcard_action
import logging

logger = logging.getLogger(__name__)


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):

    list_display = ("question", "category", "source")
    search_fields = ("question", "answer", "category")
    list_filter = ("state", "category", "created_at")

    @log_flashcard_action("Delete flashcard")
    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
            logger.info(f"Flashcard '{obj}' has been deleted by user {request.user}.")
        except Exception as e:
            logger.error(f"Error during deleting flashcard '{obj}': {e}")
