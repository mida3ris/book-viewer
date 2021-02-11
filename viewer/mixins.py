from django.contrib import messages
from django.urls import reverse


class MessageMixin:
    """Separate mixin for adding messages to the pages.
    """
    success_message = None
    error_message = None

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message, extra_tags='danger')
        return super().form_invalid(form)

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)


class RedirectMixin:
    """Mixin for adding support to redirect by url pattern name.
    """
    redirect_url_pattern = None

    def get_success_url(self) -> str:
        if self.redirect_url_pattern:
            return reverse(self.redirect_url_pattern, args=(self.object.pk,))
        return self.success_url
