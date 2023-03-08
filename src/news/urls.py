from django.urls import re_path

from src.news import views

app_name = "news"

urlpatterns = [
    re_path(r"^$", views.NewsListView.as_view(), name="list"),
    re_path(r"^like/$", views.like, name="like_post"),
    re_path(r"^delete/(?P<pk>[-\w]+)/$", views.NewsDeleteView.as_view(), name="delete_news"),
    re_path(r"^get-thread/$", views.get_thread, name="get_thread"),
    re_path(r"^post-news/$", views.post_news, name="post_news"),
    re_path(r"^post-comment/$", views.post_comment, name="post_comments"),
    re_path(r"^update-interactions/$", views.update_interactions, name="update_interactions"),
]
