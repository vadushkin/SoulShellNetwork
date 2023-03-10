import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import models
from django.urls import reverse

from src.notifications.models import notification_handler, Notification


class News(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="publisher",
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="thread",
    )
    content = models.TextField(max_length=280)
    liked = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="liked_news",
    )
    reply = models.BooleanField(verbose_name="Is a reply?", default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.reply:
            channel_layer = get_channel_layer()
            payload = {
                "type": "receive",
                "key": "additional_news",
                "actor_name": self.user.username,
            }
            async_to_sync(channel_layer.group_send)("notifications", payload)

    def __str__(self):
        return str(self.content)

    def get_absolute_url(self):
        return reverse("news:detail", kwargs={"uuid_id": self.uuid})

    def switch_like(self, user):
        if user in self.liked.all():
            self.liked.remove(user)
        else:
            self.liked.add(user)

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            return self

    def reply_this(self, user, text):
        parent = self.get_parent()
        reply_news = News.objects.create(
            user=user,
            content=text,
            reply=True,
            parent=parent,
        )
        notification_handler(
            user,
            parent.user,
            Notification.REPLY,
            action_object=reply_news,
            id_value=str(parent.uuid_id),
            key="social_update",
        )

    def get_thread(self):
        parent = self.get_parent()
        return parent.thread.all()

    def count_thread(self):
        return self.get_thread().count()

    def count_likers(self):
        return self.liked.count()

    def get_likers(self):
        return self.liked.all()

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ("-timestamp",)
