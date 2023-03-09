import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction


class MessageQuerySet(models.query.QuerySet):
    def get_conversation(self, sender, recipient):
        qs_one = self.filter(sender=sender, recipient=recipient)
        qs_two = self.filter(sender=recipient, recipient=sender)

        return qs_one.union(qs_two).order_by("timestamp")

    def get_most_recent_conversation(self, recipient):
        try:
            qs_sent = self.filter(sender=recipient)
            qs_received = self.filter(recipient=recipient)

            qs = qs_sent.union(qs_received).latest("timestamp")

            if qs.sender == recipient:
                return qs.recipient

            return qs.sender

        except self.model.DoesNotExist:
            return get_user_model().objects.get(username=recipient.username)

    def mark_conversation_as_read(self, sender, recipient):
        qs = self.filter(sender=sender, recipient=recipient)
        return qs.update(unread=False)


class Message(models.Model):
    objects = MessageQuerySet.as_manager()

    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_messages",
        verbose_name="Sender",
        null=True,
        on_delete=models.SET_NULL,
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_messages",
        null=True,
        blank=True,
        verbose_name="Recipient",
        on_delete=models.SET_NULL,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(max_length=1000, blank=True)
    unread = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ("-timestamp",)

    def __str__(self):
        return self.message

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    @staticmethod
    def send_message(sender, recipient, message):
        new_message = Message.objects.create(
            sender=sender, recipient=recipient, message=message,
        )
        channel_layer = get_channel_layer()
        payload = {
            "type": "receive",
            "key": "message",
            "message_id": str(new_message.uuid_id),
            "sender": str(sender),
            "recipient": str(recipient),
        }
        transaction.on_commit(
            lambda: async_to_sync(channel_layer.group_send)(recipient.username, payload)
        )
        return new_message
