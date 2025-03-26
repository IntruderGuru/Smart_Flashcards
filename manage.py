#!/usr/bin/env python
"""
Narzędzie wiersza poleceń Django do zarządzania aplikacją.
"""

import os
import sys


def main():
    """
    Uruchamia zadania administracyjne Django.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flashcards_app.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Nie można zaimportować Django. Czy Django jest zainstalowane "
            "i dostępne w zmiennej środowiskowej PYTHONPATH? "
            "Sprawdź również, czy wirtualne środowisko jest aktywne."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
