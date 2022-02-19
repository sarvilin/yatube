import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    current_year = datetime.datetime.now().year
    return {
        'year': current_year,
    }
