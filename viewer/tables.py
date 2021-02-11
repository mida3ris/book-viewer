from collections import Collection

from dev_tools.template.components import BaseButton
from dev_tools.template.mixins import HttpRequestType
from django.db.models import Count
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from template_tables.components import (BaseTemplateTable, TableRowType, TR, TH as BTH, TD, TemplateTablePagination,
                                        AbstractTableElement, BaseHtmlElementWithSlots)

from viewer.models import Bookcase, Book, BookAuthor, BookcaseSlot


class BookPicture(AbstractTableElement, BaseHtmlElementWithSlots):
    """Class for rendering images in table cells.
    """
    html_string = '<%(tag)s %(html_params)s />'
    default_css_classes = ['uk-border-rounded']
    default_html_params = {'width': '80', 'height': '80'}
    tag = 'img'

    def __init__(self, html_params: dict = None):
        super().__init__('', None, html_params)


class TableLink(BaseButton):
    """Class for rendering buttons in table cells.
    """
    tag = 'a'
    default_css_classes = ['bv-action-link']


class TH(BTH):
    """Custom implementation of table header cell.
    """
    order = '<%(tag)s %(html_params)s>%(data)s<a href="%(ordering_url)s" uk-icon="%(order_direction)s"></a></%(tag)s>'
    order_classes = {
        True: 'arrow-down',
        False: 'arrow-up'
    }


class TablePagination(TemplateTablePagination):
    """Custom implementation of table pagination.
    """
    css_classes = ['uk-pagination']
    template = 'blocks/_uikit_table_pagination.html'


class BaseTable(BaseTemplateTable):
    """Custom table as a parent for all project tables.
    """
    css_classes = ['uk-table uk-table-hover uk-table-divider uk-table-responsive']
    empty_table_text = _('No items found')


class BookTable(BaseTable):
    """Table view for to display books info.
    """
    def get_header_rows(self) -> list['TableRowType']:
        return [
            TR([
                TH(_('Bookcase name'), ordering='bookcase_slot__bookcase__name'),
                TH(_('Bookshelf'), ordering='bookcase_slot__bookshelf_number'),
                TH(_('Book slot'), ordering='bookcase_slot__number'),
                TH(_('Book name'), ordering='name'),
                TH(_('Author'), ordering='author__firstname'),
                TH(_('Picture')),
                TH('', css_classes=['bv-action-cell'])
            ])
        ]

    def get_body_row(self, index: int, data_item: 'Book') -> 'TableRowType':
        edit_btn = TableLink(
            html_params={
                'uk-icon': 'pencil',
                'href': reverse('viewer:book_update', kwargs=dict(pk=data_item.pk))
            }
        ).render()
        delete_btn = TableLink(
            html_params={
                'uk-icon': 'trash',
                'href': reverse('viewer:book_delete', kwargs=dict(pk=data_item.pk))
            }
        ).render()
        book_picture = BookPicture(html_params={'src': data_item.picture.url}).render() if data_item.picture else None
        return TR([
            TD(data_item.bookcase_slot.bookcase.name),
            TD(data_item.bookcase_slot.bookshelf_number),
            TD(data_item.bookcase_slot.number),
            TD(data_item.name),
            TD(data_item.author),
            TD(book_picture),
            TD(edit_btn + delete_btn)
        ])


class BookcaseTable(BaseTable):
    """Table view for to display bookcase info.
    """
    def __init__(self, request: 'HttpRequestType', object_list: Collection):
        # aggregation with grouping for slots calculation.
        bookcase_slots = (
            BookcaseSlot
            .objects
            .values('bookcase_id')
            .filter(bookcase_id__in=tuple(obj.id for obj in object_list))
            .annotate(total=Count('id'))
        )
        self.total_slots = {obj['bookcase_id']: obj['total'] for obj in bookcase_slots}
        super().__init__(request, object_list)

    def get_header_rows(self) -> list['TableRowType']:
        return [
            TR([
                TH(_('Bookcase name'), ordering='name'),
                TH(_('Bookcase slots')),
                TH('', css_classes=['bv-action-cell'])
            ])
        ]

    def get_body_row(self, index: int, data_item: 'Bookcase') -> 'TableRowType':
        edit_btn = TableLink(
            html_params={
                'uk-icon': 'pencil',
                'href': reverse('viewer:bookcase_update', kwargs=dict(pk=data_item.pk))
            }
        ).render()
        delete_btn = TableLink(
            html_params={
                'uk-icon': 'trash',
                'href': reverse('viewer:bookcase_delete', kwargs=dict(pk=data_item.pk))
            }
        ).render()
        return TR([
            TD(data_item.name),
            TD(self.total_slots.get(data_item.id)),
            TD(edit_btn + delete_btn)
        ])


class BookAuthorTable(BaseTable):
    """Table view for to display books authors info.
    """
    def get_header_rows(self) -> list['TableRowType']:
        return [
            TR([
                TH(_('First name'), ordering='firstname'),
                TH(_('Last name'), ordering='lastname'),
                TH('', css_classes=['bv-action-cell'])
            ])
        ]

    def get_body_row(self, index: int, data_item: 'BookAuthor') -> 'TableRowType':
        edit_btn = TableLink(
            html_params={
                'uk-icon': 'pencil',
                'href': reverse('viewer:book_author_update', kwargs=dict(pk=data_item.pk))
            }
        ).render()
        delete_btn = TableLink(
            html_params={
                'uk-icon': 'trash',
                'href': reverse('viewer:book_author_delete', kwargs=dict(pk=data_item.pk))
            }
        ).render()
        return TR([
            TD(data_item.firstname),
            TD(data_item.lastname),
            TD(edit_btn + delete_btn)
        ])
