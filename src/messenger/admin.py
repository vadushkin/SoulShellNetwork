from django.contrib import admin

from src.messenger.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "timestamp")
    list_filter = ("sender", "recipient")
