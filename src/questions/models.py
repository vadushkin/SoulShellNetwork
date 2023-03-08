from collections import Counter
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from slugify import slugify
from taggit.managers import TaggableManager


class Vote(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.BooleanField(default=True)
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="votes_on",
        on_delete=models.CASCADE,
    )
    object_id = models.CharField(max_length=50, blank=True, null=True)
    vote = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        index_together = ("content_type", "object_id")
        unique_together = ("user", "content_type", "object_id")


class QuestionQuerySet(models.query.QuerySet):
    def get_answered(self):
        return self.filter(has_answer=True)

    def get_unanswered(self):
        return self.filter(has_answer=False)

    def get_counted_tags(self):
        tag_dict = {}
        query = self.all().annotate(tagged=Count("tags")).filter(tags__gt=0)

        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1

        return tag_dict.items()


class Question(models.Model):
    """Model class to contain every question in the forum."""

    OPEN = "O"
    CLOSED = "C"
    DRAFT = "D"

    STATUS = ((OPEN, "Open"), (CLOSED, "Closed"), (DRAFT, "Draft"))

    objects = QuestionQuerySet.as_manager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True, blank=False)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    content = MarkdownxField()
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    has_answer = models.BooleanField(default=False)
    votes = GenericRelation(Vote)
    total_votes = models.IntegerField(default=0)
    tags = TaggableManager()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.title}-{self.id}", lowercase=True, max_length=80,
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def count_answers(self):
        return Answer.objects.filter(question=self).count()

    def count_votes(self):
        """Method to update the sum of the total votes. Uses this complex query
        to avoid race conditions at database level."""
        dic = Counter(self.votes.values_list("value", flat=True))
        Question.objects.filter(id=self.id).update(total_votes=dic[True] - dic[False])
        self.refresh_from_db()

    def get_upvoters(self):
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        return [vote.user for vote in self.votes.filter(value=False)]

    def get_answers(self):
        return Answer.objects.filter(question=self)

    def get_accepted_answer(self):
        return Answer.objects.get(question=self, is_answer=True)

    def get_markdown(self):
        return markdownify(self.content)


class Answer(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = MarkdownxField()
    votes = GenericRelation(Vote)
    total_votes = models.IntegerField(default=0)
    is_answer = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_answer", "-timestamp"]
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def count_votes(self):
        """Method to update the sum of the total votes. Uses this complex query
        to avoid race conditions at database level."""
        dic = Counter(self.votes.values_list("value", flat=True))
        Answer.objects.filter(uuid_id=self.uuid_id).update(total_votes=dic[True] - dic[False])
        self.refresh_from_db()

    def get_upvoters(self):
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        return [vote.user for vote in self.votes.filter(value=False)]

    def accept_answer(self):
        answer_set = Answer.objects.filter(question=self.question)
        answer_set.update(is_answer=False)

        self.is_answer = True
        self.save()

        self.question.has_answer = True
        self.question.save()
