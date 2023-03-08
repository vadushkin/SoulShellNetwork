from django.contrib import admin

from src.news.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("content", "user", "reply")
    list_filter = ("timestamp", "reply")
