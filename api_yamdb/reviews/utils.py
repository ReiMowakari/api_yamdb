from datetime import datetime


def get_current_year() -> int:
    """Возвращает текущий год."""
    return datetime.today().year
