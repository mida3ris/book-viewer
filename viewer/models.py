from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from viewer.managers import BookQuerySet


class Bookcase(models.Model):
    """A bookcase model for grouping shelves with books.
    """
    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('Bookcase name'), max_length=254)

    class Meta:
        verbose_name = _('Bookcase')
        verbose_name_plural = _('Bookcases')
        unique_together = (
            ('user', 'name'),
        )

    def __str__(self):
        return self.name


class BookcaseSlot(models.Model):
    """Model to store book placement in the bookcase.
    """
    bookcase = models.ForeignKey('viewer.Bookcase', verbose_name=_('Bookcase'), related_name='slots',
                                 on_delete=models.CASCADE)
    bookshelf_number = models.PositiveIntegerField(verbose_name=_('Bookshelf number'))
    number = models.PositiveIntegerField(verbose_name=_('Slot number'))

    class Meta:
        verbose_name = _('Bookcase slot')
        verbose_name_plural = _('Bookcase slots')
        unique_together = (
            ('bookcase', 'bookshelf_number', 'number'),
        )

    def __str__(self):
        return f'{self.bookcase.name}:{self.bookshelf_number}:{self.number}'

    @classmethod
    def bulk_create_for_bookcase(cls, bookcase: 'Bookcase', bookshelf_count: int, bookshelf_capacity: int) -> None:
        batch = [
            cls(
                bookcase=bookcase,
                bookshelf_number=shelf_number + 1,
                number=slot_number + 1
            ) for shelf_number in range(bookshelf_count) for slot_number in range(bookshelf_capacity)
        ]
        cls.objects.bulk_create(batch)


class BookAuthor(models.Model):
    """A book author model.
    """
    firstname = models.CharField(verbose_name=_('First name'), max_length=254)
    lastname = models.CharField(verbose_name=_('Last name'), max_length=254)

    class Meta:
        verbose_name = _('Book author')
        verbose_name_plural = _('Book authors')
        unique_together = (
            ('firstname', 'lastname'),
        )

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Book(models.Model):
    """A book model.
    """
    bookcase_slot = models.OneToOneField('viewer.BookcaseSlot', verbose_name=_('Bookcase slot'), related_name='book',
                                         null=True, on_delete=models.SET_NULL)
    author = models.ForeignKey('viewer.BookAuthor', verbose_name=_('Book author'), related_name='books',
                               on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('Book name'), max_length=254)
    picture = models.ImageField(verbose_name=_('Book picture'), blank=True, null=True)

    objects = BookQuerySet.as_manager()

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')

    def __str__(self):
        return f'{self.name} - {self.author}'
