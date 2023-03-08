from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models
from django.db.models import Count
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from slugify import slugify

from taggit.managers import TaggableManager


class ArticleQuerySet(models.query.QuerySet):
    def get_published(self):
        return self.filter(status="P")

    def get_drafts(self):
        return self.filter(status="D")

    def get_counted_tags(self):
        tag_dict = {}
        query = (
            self.filter(status="P").annotate(tagged=Count("tags")).filter(tags__gt=0)
        )

        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1

        return tag_dict.items()


class Article(models.Model):
    DRAFT = "D"
    PUBLISHED = "P"
    STATUS = ((DRAFT, "Draft"), (PUBLISHED, "Published"))

    objects = ArticleQuerySet.as_manager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="author",
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=255, null=False, unique=True)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    image = CloudinaryField("Featured image", blank=True, null=True)
    content = MarkdownxField()
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    edited = models.BooleanField(default=False)
    tags = TaggableManager()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ("-timestamp",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.user.username}-{self.title}", lowercase=True, max_length=80,
            )

        super().save(*args, **kwargs)

    def get_markdown(self):
        return markdownify(self.content)
