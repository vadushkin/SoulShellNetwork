from django.contrib import admin
from django.urls import path, include

# from django.views.generic import TemplateView

urlpatterns = [
    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("users/", include("src.users.urls", namespace="users")),
    path("news/", include("src.news.urls", namespace="news")),
    path("messenger/", include("src.messenger.urls", namespace="messenger")),
    path("search/", include("src.search.urls", namespace="search")),
    path("articles/", include("src.articles.urls", namespace="articles")),
    path("questions/", include("src.questions.urls", namespace="questions")),
    # path(r"accounts/", include("allauth.urls")),
]
