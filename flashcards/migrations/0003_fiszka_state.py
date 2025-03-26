# Generated by Django 5.1.3 on 2024-12-16 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flashcards", "0002_Flashcard_created_at_Flashcard_updated_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="Flashcard",
            name="state",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("published", "Published"),
                    ("archived", "Archived"),
                ],
                default="draft",
                max_length=20,
                verbose_name="Stan",
            ),
        ),
    ]
