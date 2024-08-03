from django.forms import ValidationError

from api_yamdb.settings import MIN_YEAR
from reviews.utils import get_current_year

INCORRECT_TITLE_YEAR = 'Введите иной год'


def validate_year(year: int):
    """Валидация поля year."""
    current_year = get_current_year()
    if not (MIN_YEAR <= year <= current_year):
        raise ValidationError(INCORRECT_TITLE_YEAR)
