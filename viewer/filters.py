from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, OrderingFilter, CharFilter

from viewer.forms import StyledFormMixin
from viewer.models import Book, Bookcase, BookAuthor


class StyledFilterForm(StyledFormMixin, forms.Form):
    """Styled form for filters.
    """
    submit_text = _('Search')


class BookFilter(FilterSet):
    """Filter class for book filter view.
    """
    _order_fields = [
        'bookcase_slot__bookcase__name',
        'bookcase_slot__bookshelf_number',
        'bookcase_slot__number',
        'name',
        'author__firstname'
    ]
    ordering = OrderingFilter(
        fields=tuple(
            (field_name, field_name) for field_name in _order_fields
        )
    )

    bookcase_name = CharFilter(label=_('Bookcase name'), field_name='bookcase_slot__bookcase__name',
                               lookup_expr='icontains')
    author_name = CharFilter(label=_('Author name'), method='author_filter')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['bookcase_slot__bookshelf_number'].label = _('Bookshelf')
        self.form.fields['bookcase_slot__bookshelf_number'].widget.attrs['mine'] = 1
        self.form.fields['bookcase_slot__number'].label = _('Book slot')
        self.form.fields['bookcase_slot__number'].widget.attrs['min'] = 1

    class Meta:
        model = Book
        fields = [
            'bookcase_slot__bookshelf_number',
            'bookcase_slot__number',
            'name'
        ]
        form = StyledFilterForm

    def author_filter(self, queryset, name, value):
        return queryset.filter(Q(author__firstname__icontains=value) | Q(author__lastname__icontains=value))


class BookcaseFilter(FilterSet):
    """Filter class for bookcase filter view.
    """
    _order_fields = [
        'name'
    ]
    ordering = OrderingFilter(
        fields=tuple(
            (field_name, field_name) for field_name in _order_fields
        )
    )

    class Meta:
        model = Bookcase
        fields = [
            'name'
        ]
        form = StyledFilterForm


class BookAuthorFilter(FilterSet):
    """Filter class for book author filter view.
    """
    _order_fields = [
        'firstname',
        'lastname'
    ]
    ordering = OrderingFilter(
        fields=tuple(
            (field_name, field_name) for field_name in _order_fields
        )
    )

    class Meta:
        model = BookAuthor
        fields = [
            'firstname',
            'lastname'
        ]
        form = StyledFilterForm
