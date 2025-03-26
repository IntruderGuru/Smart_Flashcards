from flashcards.services.ocr import OCRProcessor
from flashcards.services.nlp import NLPProcessor


class FlashcardFacade:
    """
    Facade for combining OCR and NLP functionalities to generate flashcards.
    """

    @staticmethod
    def generate_flashcards_from_image(image_path, category="default"):
        """
        Extracts text from an image and generates flashcards.
        """
        text = OCRProcessor.extract_text(image_path)
        if not text:
            raise ValueError("Failed to extract text from the image.")

        return FlashcardFacade.generate_flashcards_from_text(text, category)

    @staticmethod
    def generate_flashcards_from_text(text, category="default"):
        """
        Generates flashcards from raw text.
        """
        if not text.strip():
            raise ValueError("No text provided. Cannot generate flashcards.")

        # Process with NLP
        nlp_processor = NLPProcessor()
        nlp_flashcards = nlp_processor.analyze_text(text, category)

        # Combine and deduplicate flashcards
        unique_flashcards = list(
            {f"{fc.question}-{fc.answer}": fc for fc in nlp_flashcards}.values()
        )

        # Return flashcards without saving
        return unique_flashcards
