from django.contrib import admin
from django.urls import path, include
# from django.views.generic import TemplateView

urlpatterns = [
    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("users/", include("src.users.urls", namespace="users")),
    # path(r"accounts/", include("allauth.urls")),
]
