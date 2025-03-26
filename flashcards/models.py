from django.db import models
from django.utils.timezone import now


class Flashcard(models.Model):
    """
    Model representing a flashcard.
    """

    STATE_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    question = models.TextField(verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")
    category = models.CharField(max_length=200, blank=True, verbose_name="Category")
    source = models.CharField(max_length=200, blank=True, verbose_name="Source")
    state = models.CharField(
        max_length=20, choices=STATE_CHOICES, default="draft", verbose_name="State"
    )
    created_at = models.DateTimeField(default=now, verbose_name="Date of creation")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date of update")
    correct_answers = models.IntegerField(default=0, verbose_name="Correct answers")
    incorrect_answers = models.IntegerField(default=0, verbose_name="Incorrect answers")

    def __str__(self):
        return (
            f"Flashcard: {self.question[:50]} - Category: {self.category or 'General'}"
        )

    def update_statistics(self, correct):
        """
        Updates flashcard statistics based on the answer correctness.
        """
        if correct:
            self.correct_answers += 1
        else:
            self.incorrect_answers += 1
        self.save()
