import logging
from functools import wraps

logger = logging.getLogger(__name__)


def log_flashcard_action(action):
    """
    Decorator for logging flashcard actions.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Started action: {action}")
            result = func(*args, **kwargs)
            logger.info(f"Finished action: {action}")
            return result

        return wrapper

    return decorator
