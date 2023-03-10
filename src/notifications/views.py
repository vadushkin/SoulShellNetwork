from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from src.notifications.models import Notification


class NotificationUnreadListView(LoginRequiredMixin, ListView):
    model = Notification
    context_object_name = "notification_list"
    template_name = "notifications/notification_list.html"

    def get_queryset(self, **kwargs):
        return self.request.user.notifications.unread()


@login_required
def mark_all_as_read(request):
    request.user.notifications.mark_all_as_read()
    request_next = request.GET.get("next")
    messages.add_message(
        request,
        messages.SUCCESS,
        f"All notifications to {request.user.username} have been marked as read.",
    )

    if request_next:
        return redirect(request_next)

    return redirect("notifications:unread")


@login_required
def mark_as_read(request, slug=None):
    if slug:
        notification = get_object_or_404(Notification, slug=slug)
        notification.mark_as_read()
        notification_slug = notification.slug
    else:
        notification_slug = "<no slug>"

    messages.add_message(
        request,
        messages.SUCCESS,
        f"The notification {notification_slug} has been marked as read.",
    )

    request_next = request.GET.get("next")

    if request_next:
        return redirect(request_next)

    return redirect("notifications:unread")


@login_required
def get_latest_notifications(request):
    notifications = request.user.notifications.get_most_recent()
    return render(
        request, "notifications/most_recent.html", {"notifications": notifications}
    )
