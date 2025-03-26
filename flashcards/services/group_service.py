from flashcards.models import Flashcard


class GroupService:

    @staticmethod
    def get_categories():
        categories = Flashcard.objects.values_list("category", flat=True).distinct()

        # Debugging: Print extracted categories before filtering
        print(f"DEBUG: Raw categories from DB: {list(categories)}")

        categories = [cat if cat else "General" for cat in categories]

        # Debugging: Print processed categories
        print(f"DEBUG: Processed categories: {categories}")

        return sorted(categories)

    @staticmethod
    def get_flashcards_by_category(category):
        """
        Returns flashcards for a specific category.
        """
        if category == "General":
            return Flashcard.objects.filter(category__in=["", None])
        return Flashcard.objects.filter(category=category)
