from django.db.models import QuerySet


class BookQuerySet(QuerySet):
    """QuerySet for book model.
    """
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs).select_related('bookcase_slot__bookcase', 'author')
