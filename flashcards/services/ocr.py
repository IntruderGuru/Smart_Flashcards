import logging
from PIL import Image
import pytesseract
from typing import List, Optional
from django.db import IntegrityError
from ..models import Flashcard

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Class for processing images and generating flashcards.
    """

    @staticmethod
    def extract_text(image_path: str) -> str:
        """
        Extracts text from an image using pytesseract.

        Args:
            image_path (str): The file path to the image.

        Returns:
            str: The extracted text. Returns an empty string if extraction fails.
        """
        try:
            logger.info(f"Starting text extraction from image: {image_path}")
            image = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(image, lang="pol")
            logger.info(f"Completed text extraction:\n{extracted_text}")
            return extracted_text
        except FileNotFoundError:
            logger.error(f"File not found: {image_path}")
            return ""
        except Exception as e:
            logger.exception(f"OCR error while processing image {image_path}: {e}")
            return ""

    @staticmethod
    def analyze_text_and_generate_flashcards(
        text: str, category: str = "default"
    ) -> List[Flashcard]:
        """
        Analyzes text and generates flashcards based on text structure.

        Args:
            text (str): The text to analyze.
            category (str, optional): The category for the flashcards. Defaults to "default".

        Returns:
            List[Flashcard]: A list of generated Flashcard instances.
        """
        if not text.strip():
            logger.warning("Empty text provided for analysis. No flashcards generated.")
            return []

        flashcards = []
        lines = text.split("\n")
        current_question: Optional[str] = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.isupper():
                current_question = line
                logger.debug(f"Detected question: {current_question}")
            elif current_question:
                # Create flashcards based on the detected question and answer
                flashcard = Flashcard(
                    question=current_question,
                    answer=line,
                    category=category,
                )
                flashcards.append(flashcard)
                logger.debug(
                    f"Created flashcard: Q='{flashcard.question}' A='{flashcard.answer}'"
                )
                current_question = (
                    None  # Reset the current question after adding a flashcard
                )

        if flashcards:
            try:
                Flashcard.objects.bulk_create(flashcards)
                logger.info(f"Saved {len(flashcards)} flashcards to the database.")
            except IntegrityError as e:
                logger.error(f"Database error while saving flashcards: {e}")
        else:
            logger.warning("No flashcards were generated from the provided text.")

        return flashcards
