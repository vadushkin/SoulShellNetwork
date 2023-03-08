from django.urls import re_path

from src.articles.views import (
    ArticlesListView,
    DraftsListView,
    CreateArticleView,
    EditArticleView,
    DetailArticleView,
)

app_name = "articles"

urlpatterns = [
    re_path(r"^$", ArticlesListView.as_view(), name="list"),
    re_path(r"^write-new-article/$", CreateArticleView.as_view(), name="write_new"),
    re_path(r"^drafts/$", DraftsListView.as_view(), name="drafts"),
    re_path(r"^edit/(?P<pk>\d+)/$", EditArticleView.as_view(), name="edit_article"),
    re_path(r"^(?P<slug>[-\w]+)/$", DetailArticleView.as_view(), name="article"),
]
