from django.contrib import admin
from django.contrib.admin import ModelAdmin

from viewer.models import Bookcase, Book, BookAuthor, BookcaseSlot

admin.site.register(Bookcase, ModelAdmin)
admin.site.register(BookcaseSlot, ModelAdmin)
admin.site.register(BookAuthor, ModelAdmin)
admin.site.register(Book, ModelAdmin)
