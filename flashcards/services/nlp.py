import openai
import logging
import os
import re
from ..models import Flashcard

logger = logging.getLogger(__name__)


class NLPProcessor:

    def __init__(self):
        """
        Initializes the NLP processor by fetching the OpenAI API key from environment variables.
        """
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("No OpenAI key, cannot perform analysis.")

    def analyze_text(self, text, category="default"):
        logger.info(f"Started text analysys")
        if not text.strip():
            logger.warning("Empty string - cannot generate flashcards")
            return []

        try:
            return self._generate_flashcards(text, category)
        except (
            openai.APIError or openai.APIConnectionError or openai.RateLimitError
        ) as e:
            logger.error(f"Error generating flashcards: API Error {e}")
            raise ValueError("Error generating flashcards: API Error")
        except Exception as e:
            logger.exception(f"Error generating flashcards: API Error {e}")
            raise RuntimeError("Error generating flashcards: API Error")

    def _generate_flashcards(self, text, category):
        logger.debug("Prepering a request to OpenAI API.")
        system_message = (
            "You are a helpfull assitent and your mission is generating flashcards."
        )
        user_message = f"""
        Analyze the text and generate flashcards in the same language, the fromat is: 
        question: [question]
        answer: [answer]
        ---
        Text:
        {text}
        """

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1024,
            temperature=0.7,
        )

        generated_text = response.choices[0].message.content.strip()
        logger.debug(f"Answer OpenAI: {generated_text}")

        flashcards = []
        pattern = r"(?i)question:\s*(.*?)\s*answer:\s*(.*?)(?:\s*---|$)"
        matches = re.findall(pattern, generated_text, re.DOTALL)

        logger.debug(f"OpenAI answer: {matches}")

        for question, answer in matches:
            flashcard = Flashcard(
                question=question.strip(),
                answer=answer.strip(),
                category=category,
            )
            flashcards.append(flashcard)
            logger.debug(f" Flashcard: {flashcard}")

        return flashcards
