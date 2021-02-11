from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from template_tables.mixins import TemplateTableViewMixin, TemplateTablePaginationMixin

from viewer.filters import BookFilter, BookcaseFilter, BookAuthorFilter
from viewer.forms import LoginForm, BookcaseCreateForm, BookForm, BookAuthorForm, BookcaseEditForm
from viewer.mixins import MessageMixin, RedirectMixin
from viewer.models import Bookcase, Book, BookAuthor, BookcaseSlot
from viewer.tables import BookcaseTable, TablePagination, BookTable, BookAuthorTable


class CustomLoginView(LoginView):
    """Django's login view with custom form.
    """
    form_class = LoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True


BOOKS = 'books'
BOOKCASES = 'bookcases'
BOOK_AUTHORS = 'authors'


class DashboardViewMixin(LoginRequiredMixin):
    """Mixin for dashboard views.
    """
    menu: dict = {
        BOOKS: {
            'url': reverse_lazy('viewer:book_list'),
            'icon': 'list',
            'name': _('Books'),
            'add_divider': True
        },
        BOOKCASES: {
            'url': reverse_lazy('viewer:bookcase_list'),
            'icon': 'table',
            'name': _('Bookcases')
        },
        BOOK_AUTHORS: {
            'url': reverse_lazy('viewer:book_author_list'),
            'icon': 'user',
            'name': _('Authors')
        }
    }
    alias: str = None
    actions: list[dict] = []
    ordering = ('-id',)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data( object_list=object_list, **kwargs)
        context.update({
            'actions': self.get_actions(),
            'menu': self.menu,
            'alias': self.alias,
        })
        return context

    def get_actions(self) -> list[dict]:
        return self.actions


class DashboardFilterView(DashboardViewMixin, FilterView):
    """Base list view for dashboard with predefined actions.
    """
    pass


class BookListView(TemplateTableViewMixin, TemplateTablePaginationMixin, DashboardFilterView):
    """View for rendering book's table.
    """
    model = Book
    pagination_class = TablePagination
    filterset_class = BookFilter
    table_class = BookTable
    template_name = 'dashboard_list.html'

    alias = BOOKS
    actions = [
        {
            'url': reverse_lazy('viewer:book_add'),
            'icon': 'plus',
            'name': _('Add book')
        }
    ]

    def get_queryset(self):
        return super().get_queryset().filter(bookcase_slot__bookcase__user=self.request.user)


class BookcaseListView(TemplateTableViewMixin, TemplateTablePaginationMixin, DashboardFilterView):
    """View for rendering bookcase's table.
    """
    model = Bookcase
    pagination_class = TablePagination
    filterset_class = BookcaseFilter
    table_class = BookcaseTable
    template_name = 'dashboard_list.html'

    alias = BOOKCASES
    actions = [
        {
            'url': reverse_lazy('viewer:bookcase_add'),
            'icon': 'plus',
            'name': _('Add bookcase')
        }
    ]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class BookAuthorListView(TemplateTableViewMixin, TemplateTablePaginationMixin, DashboardFilterView):
    """View for rendering book author's table.
    """
    model = BookAuthor
    pagination_class = TablePagination
    filterset_class = BookAuthorFilter
    table_class = BookAuthorTable
    template_name = 'dashboard_list.html'

    alias = BOOK_AUTHORS
    actions = [
        {
            'url': reverse_lazy('viewer:book_author_add'),
            'icon': 'plus',
            'name': _('Add author')
        }
    ]


class CreateOrUpdateMixinView(MessageMixin, RedirectMixin):
    """Mixin for additional logic on objects create or update events.
    """
    success_message = _('Success!')
    error_message = _('Something went wrong. Please check form errors')

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({
            'user': self.request.user
        })
        return form_kwargs


class DeleteMixinView(MessageMixin, RedirectMixin):
    """Mixin to provide custom logic on objects deletion.
    """
    success_message = _('Deleted successfully!')
    confirmation_text = _('Are you sure you want to delete this object?')
    submit_text = _('Delete object')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({
            'confirmation_text': self.confirmation_text,
            'submit_text': self.submit_text
        })
        return context


class BookCreateView(DashboardViewMixin, CreateOrUpdateMixinView, CreateView):
    """View for bookcase creation.
    """
    model = Book
    context_object_name = 'book'
    form_class = BookForm
    template_name = 'dashboard_form.html'
    success_url = reverse_lazy('viewer:book_list')

    alias = BOOKS


class BookUpdateView(DashboardViewMixin, CreateOrUpdateMixinView, UpdateView):
    """View for book update.
    """
    model = Book
    context_object_name = 'book'
    form_class = BookForm
    template_name = 'dashboard_form.html'
    redirect_url_pattern = 'viewer:book_update'

    alias = BOOKS


class BookDeleteView(DashboardViewMixin, DeleteMixinView, DeleteView):
    """View for book deletion.
    """
    model = Book
    context_object_name = 'book'
    success_url = reverse_lazy('viewer:book_list')
    template_name = 'dashboard_confirm.html'

    alias = BOOKS


class BookcaseCreateView(DashboardViewMixin, CreateOrUpdateMixinView, CreateView):
    """View for bookcase creation.
    """
    model = Bookcase
    context_object_name = 'bookcase'
    form_class = BookcaseCreateForm
    template_name = 'dashboard_form.html'
    success_url = reverse_lazy('viewer:bookcase_list')

    alias = BOOKCASES

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            BookcaseSlot.bulk_create_for_bookcase(
                bookcase=self.object,
                bookshelf_count=form.cleaned_data['shelf_count'],
                bookshelf_capacity=form.cleaned_data['shelf_capacity']
            )
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


class BookcaseUpdateView(DashboardViewMixin, CreateOrUpdateMixinView, UpdateView):
    """View for bookcase update.
    """
    model = Bookcase
    context_object_name = 'bookcase'
    form_class = BookcaseEditForm
    template_name = 'dashboard_form.html'
    redirect_url_pattern = 'viewer:bookcase_update'

    alias = BOOKCASES


class BookcaseDeleteView(DashboardViewMixin, DeleteMixinView, DeleteView):
    """View for bookcase deletion.
    """
    model = Bookcase
    context_object_name = 'bookcase'
    success_url = reverse_lazy('viewer:bookcase_list')
    template_name = 'dashboard_confirm.html'

    alias = BOOKCASES


class BookAuthorCreateView(DashboardViewMixin, CreateOrUpdateMixinView, CreateView):
    """View for book author creation.
    """
    model = BookAuthor
    context_object_name = 'book_author'
    form_class = BookAuthorForm
    template_name = 'dashboard_form.html'
    success_url = reverse_lazy('viewer:book_author_list')

    alias = BOOK_AUTHORS


class BookAuthorUpdateView(DashboardViewMixin, CreateOrUpdateMixinView, UpdateView):
    """View for book author update.
    """
    model = BookAuthor
    context_object_name = 'book_author'
    form_class = BookAuthorForm
    template_name = 'dashboard_form.html'
    redirect_url_pattern = 'viewer:book_author_update'

    alias = BOOK_AUTHORS


class BookAuthorDeleteView(DashboardViewMixin, DeleteMixinView, DeleteView):
    """View for book author deletion.
    """
    model = BookAuthor
    context_object_name = 'book_author'
    success_url = reverse_lazy('viewer:book_author_list')
    template_name = 'dashboard_confirm.html'

    alias = BOOK_AUTHORS
