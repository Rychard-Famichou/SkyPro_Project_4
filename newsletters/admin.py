from django.contrib import admin

from newsletters.models import Newsletter, Message


# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('owner', 'subject')
    search_fields = ('owner', 'subject')
    list_filter = ('owner', 'subject')
