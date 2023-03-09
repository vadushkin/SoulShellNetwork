from django.urls import re_path

from src.messenger import views

app_name = "messenger"

urlpatterns = [
    re_path(r"^$", views.MessagesListView.as_view(), name="messages_list"),
    re_path(r"^send-message/$", views.send_message, name="send_message"),
    re_path(r"^receive-message/$", views.receive_message, name="receive_message"),
    re_path(
        r"^(?P<username>[\w.@+-]+)/$",
        views.ConversationListView.as_view(),
        name="conversation_detail",
    ),
]
