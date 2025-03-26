from django.template.loader import render_to_string
from typing import Union
from flashcards.models import Flashcard
from gtts import gTTS
import io
from django.core.cache import cache


class FlashcardRenderer:
    """
    Design Pattern: Bridge.
    Base class for rendering flashcards in various formats.
    """

    from typing import Union

    def render(self, flashcard: Flashcard, language: str = "en") -> Union[bytes, str]:
        """
        Render the given flashcard.

        Args:
            flashcard (Flashcard): The flashcard instance to render.
            language (str): Language code for audio ('en' or 'pl').

        Returns:
            bytes or str: The rendered flashcard.
        """
        raise NotImplementedError(
            "The 'render' method must be overridden in the subclass."
        )


class TextRenderer(FlashcardRenderer):
    def render(self, flashcard: Flashcard, language: str = "en") -> str:
        if language == "pl":
            labels = ["Pytanie:", "Odpowiedź:", "Kategoria:", "Źródło:"]
        else:
            labels = ["Question:", "Answer:", "Category:", "Source:"]

        padding = max(len(label) for label in labels)  # Calculate padding dynamically

        # Format each field with dynamic padding
        output = (
            "--- Flashcard ---\n"
            f"{labels[0]} {flashcard.question}\n"
            f"{labels[1]} {flashcard.answer}\n"
            f"{labels[2]} {flashcard.category}\n"
            f"{labels[3]} {flashcard.source if flashcard.source else ''}\n"
            "-----------------"  # Separator
        )

        return output.strip()


class AudioRenderer(FlashcardRenderer):
    def render(self, flashcard: Flashcard, language: str = "en") -> bytes:
        cache_key = f"flashcard_audio_{flashcard.id}_{language}"
        audio_data = cache.get(cache_key)

        if not audio_data:
            # Generowanie treści do wypowiedzenia
            if language == "en":
                text_content = (
                    f"Question: {flashcard.question}\n"
                    f"Answer: {flashcard.answer}\n"
                    f"Category: {flashcard.category}\n"
                )
            else:
                text_content = (
                    f"Pytanie: {flashcard.question}\n"
                    f"Odpowiedź: {flashcard.answer}\n"
                    f"Kategoria: {flashcard.category}\n"
                )

            try:
                # Pierwsza próba z podanym językiem
                tts = gTTS(text=text_content, lang=language)
                first_attempt = True
            except ValueError:
                # Jeśli język jest niepoprawny, fallback do angielskiego
                text_content = (
                    f"Question: {flashcard.question}\n"
                    f"Answer: {flashcard.answer}\n"
                    f"Category: {flashcard.category}\n"
                )
                tts = gTTS(text=text_content, lang="en")
                first_attempt = False

            byte_io = io.BytesIO()
            tts.write_to_fp(byte_io)
            byte_io.seek(0)
            audio_data = byte_io.read()

            # Jeśli pierwsza próba się nie udała, powinno być drugie wywołanie write_to_fp
            if not first_attempt:
                byte_io = io.BytesIO()
                tts.write_to_fp(byte_io)
                byte_io.seek(0)
                audio_data = byte_io.read()

            cache.set(cache_key, audio_data, timeout=86400)

        return audio_data


class RendererFactory:
    """
    Factory to create appropriate FlashcardRenderer instances based on the format.
    """

    @staticmethod
    def get_renderer(format: str) -> FlashcardRenderer:
        """
        Get the appropriate renderer based on the given format.

        Args:
            format (str): The desired format ('text' or 'audio').

        Returns:
            FlashcardRenderer: An instance of the appropriate renderer.

        Raises:
            ValueError: If the format is unsupported.
        """
        format = format.lower()
        if format == "audio":
            return AudioRenderer()
        elif format == "text":
            return TextRenderer()
        else:
            raise ValueError(f"Unsupported format: {format}")


class FlashcardStandard:
    """
    Class implementing flashcard logic, separated from the rendering method.
    """

    def __init__(
        self, flashcard: Flashcard, renderer: FlashcardRenderer, language: str = "en"
    ):
        """
        Initialize the FlashcardStandard with a flashcard and a renderer.

        Args:
            flashcard (Flashcard): The flashcard instance.
            renderer (FlashcardRenderer): An instance of a renderer.
            language (str): Language code for audio ('en' or 'pl').
        """
        self.flashcard = flashcard
        self.renderer = renderer
        self.language = language

    def display(self) -> Union[bytes, str]:
        """
        Display the flashcard using the specified renderer.

        Returns:
            bytes or str: The rendered flashcard.
        """
        return self.renderer.render(self.flashcard, self.language)
