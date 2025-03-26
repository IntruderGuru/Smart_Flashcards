# flashcards/forms.py

from django import forms
from flashcards.models import Flashcard
from flashcards.services.group_service import GroupService


class FlashcardForm(forms.ModelForm):
    category_select = forms.ChoiceField(
        choices=[], required=False, label="Select Existing Category"
    )
    category_new = forms.CharField(
        max_length=100, required=False, label="Or Enter New Category"
    )

    class Meta:
        model = Flashcard
        fields = ["question", "answer", "source"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category_select"].choices = [
            (category, category) for category in GroupService.get_categories()
        ]

    def clean(self):
        cleaned_data = super().clean()
        category_select = cleaned_data.get("category_select")
        category_new = cleaned_data.get("category_new")

        if not category_select and not category_new:
            raise forms.ValidationError(
                "Please select an existing category or enter a new one."
            )

        return cleaned_data

    def save(self, commit=True):
        flashcard = super().save(commit=False)
        category_select = self.cleaned_data.get("category_select")
        category_new = self.cleaned_data.get("category_new")

        if category_new:
            flashcard.category = category_new
        elif category_select:
            flashcard.category = category_select
        else:
            flashcard.category = "default"

        if commit:
            flashcard.save()
        return flashcard
