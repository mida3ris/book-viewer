from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from viewer.models import Bookcase, Book, BookAuthor, BookcaseSlot


class StyledFormMixin:
    """Helper class for form style customization.
    """
    submit_text = _('SUBMIT')
    help_text = None
    classes = {}
    default_class = 'uk-input'
    file_fields = {}
    default_file_placeholder = _('Select file')
    icons = {}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user') if 'user' in kwargs else None
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = self.classes.get(field_name, self.default_class)
            icon = self.icons.get(field_name)
            if icon:
                field.icon = icon
            if field_name in self.file_fields:
                field.is_file_field = True
                field.file_placeholder = self.file_fields[field_name].get('placeholder', self.default_file_placeholder)


class LoginForm(StyledFormMixin, AuthenticationForm):
    """Such as 'AuthenticationForm' but with fields customization.
    """
    submit_text = _('LOGIN')
    help_text = _('Please enter your name and password to login into Book Viewer.')
    icons = {
        'username': 'user',
        'password': 'lock'
    }


class BookForm(StyledFormMixin, forms.ModelForm):
    """Custom form for creating bookcases.
    """
    classes = {
        'bookshelf': 'uk-select',
        'author': 'uk-select'
    }
    icons = {
        'name': 'pencil'
    }
    file_fields = {'picture': {}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bookcase_slot'].queryset = BookcaseSlot.objects.filter(bookcase__user=self.user)

    class Meta:
        model = Book
        fields = '__all__'


class BookcaseCreateForm(StyledFormMixin, forms.ModelForm):
    """Custom form for creating bookcases.
    """
    icons = {
        'name': 'pencil'
    }

    shelf_count = forms.IntegerField(label=_('Shelf count'), min_value=1, max_value=10)
    shelf_capacity = forms.IntegerField(label=_('Shelf capacity'), min_value=1, max_value=10)

    class Meta:
        model = Bookcase
        fields = ('name', 'shelf_count', 'shelf_capacity')


class BookcaseEditForm(StyledFormMixin, forms.ModelForm):
    """Custom form for editing bookcases.
    """
    icons = {
        'name': 'pencil'
    }

    class Meta:
        model = Bookcase
        fields = ('name',)


class BookAuthorForm(StyledFormMixin, forms.ModelForm):
    """Custom form for creating book authors.
    """
    icons = {
        'firstname': 'pencil',
        'lastname': 'pencil'
    }

    class Meta:
        model = BookAuthor
        fields = '__all__'
