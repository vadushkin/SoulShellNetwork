import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from slugify import slugify


class NotificationQuerySet(models.query.QuerySet):
    def unread(self):
        return self.filter(unread=True)

    def read(self):
        return self.filter(unread=False)

    def mark_all_as_read(self, recipient=None):
        qs = self.unread()

        if recipient:
            qs = qs.filter(recipient=recipient)

        return qs.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        qs = self.read()

        if recipient:
            qs = qs.filter(recipient=recipient)

        return qs.update(unread=True)

    def get_most_recent(self):
        return self.unread()[:5]


class Notification(models.Model):
    LIKED = "L"
    COMMENTED = "C"
    FAVORITED = "F"
    ANSWERED = "A"
    ACCEPTED_ANSWER = "W"
    EDITED_ARTICLE = "E"
    ALSO_COMMENTED = "K"
    LOGGED_IN = "I"
    LOGGED_OUT = "O"
    VOTED = "V"
    SHARED = "S"
    SIGNUP = "U"
    REPLY = "R"
    NOTIFICATION_TYPES = (
        (LIKED, "liked"),
        (COMMENTED, "commented"),
        (FAVORITED, "favorited"),
        (ANSWERED, "answered"),
        (ACCEPTED_ANSWER, "accepted"),
        (EDITED_ARTICLE, "edited"),
        (ALSO_COMMENTED, "also commented"),
        (LOGGED_IN, "logged in"),
        (LOGGED_OUT, "logged out"),
        (VOTED, "voted on"),
        (SHARED, "shared"),
        (SIGNUP, "created an account"),
        (REPLY, "replied to"),
    )

    objects = NotificationQuerySet.as_manager()

    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notify_actor",
        on_delete=models.CASCADE,
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(max_length=210, null=True, blank=True)
    unread = models.BooleanField(default=True, db_index=True)
    verb = models.CharField(max_length=1, choices=NOTIFICATION_TYPES)
    action_object_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="notify_action_object",
        on_delete=models.CASCADE,
    )
    action_object_object_id = models.CharField(max_length=50, blank=True, null=True)
    action_object = GenericForeignKey(
        "action_object_content_type",
        "action_object_object_id",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ("-timestamp",)

    def __str__(self):
        if self.action_object:
            return f"{self.actor} {self.get_verb_display()} {self.action_object} {self.time_since()} ago"

        return f"{self.actor} {self.get_verb_display()} {self.time_since()} ago"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.recipient} {self.uuid_id} {self.verb}",
                lowercase=True,
                max_length=200,
            )

        super().save(*args, **kwargs)

    def time_since(self, now=None):
        from django.utils.timesince import timesince

        return timesince(self.timestamp, now)

    def get_icon(self):
        if self.verb == "C" or self.verb == "A" or self.verb == "K":
            return "fa-comment"

        elif self.verb == "I" or self.verb == "U" or self.verb == "O":
            return "fa-users"

        elif self.verb == "L":
            return "fa-heart"

        elif self.verb == "F":
            return "fa-star"

        elif self.verb == "W":
            return "fa-check-circle"

        elif self.verb == "E":
            return "fa-pencil"

        elif self.verb == "V":
            return "fa-plus"

        elif self.verb == "S":
            return "fa-share-alt"

        elif self.verb == "R":
            return "fa-reply"

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()


def notification_handler(
        actor,
        recipient,
        verb,
        key="notification",
        id_value=None,
        action_object=None,
):
    """Handler function to create a Notification instance."""

    if recipient == "global":
        users = get_user_model().objects.all().exclude(username=actor.username)

        for user in users:
            Notification.objects.create(
                actor=actor,
                recipient=user,
                verb=verb,
                action_object=action_object,
            )
        notification_broadcast(actor, key)

    elif isinstance(recipient, list):
        for user in recipient:
            Notification.objects.create(
                actor=actor,
                recipient=get_user_model().objects.get(username=user),
                verb=verb,
                action_object=action_object,
            )

    elif isinstance(recipient, get_user_model()):
        Notification.objects.create(
            actor=actor,
            recipient=recipient,
            verb=verb,
            action_object=action_object,
        )
        notification_broadcast(
            actor,
            key,
            id_value=id_value,
            recipient=recipient.username,
        )


def notification_broadcast(actor, key, id_value=None, recipient=None):
    """Notification handler to broadcast calls to
    the reception layer of the WebSocket consumer of this app."""

    channel_layer = get_channel_layer()

    payload = {
        "type": "receive",
        "key": key,
        "actor_name": actor.username,
        "id_value": id_value,
        "recipient": recipient,
    }
    async_to_sync(channel_layer.group_send)("notifications", payload)
