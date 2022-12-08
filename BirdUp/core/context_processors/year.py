import datetime as dt

now = dt.datetime.now()


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': now.year
    }
