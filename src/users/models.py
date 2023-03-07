from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    name = models.CharField("User's name", blank=True, max_length=255)
    picture = CloudinaryField("Profile picture", blank=True, null=True)
    location = models.CharField(
        "Location", max_length=50, null=True, blank=True,
    )
    job_title = models.CharField(
        "Job title", max_length=50, null=True, blank=True,
    )
    personal_url = models.URLField(
        "Your website URL", max_length=555, blank=True, null=True,
    )
    facebook_account = models.URLField(
        "Facebook account", max_length=255, blank=True, null=True,
    )
    twitter_account = models.URLField(
        "Twitter account", max_length=255, blank=True, null=True,
    )
    github_account = models.URLField(
        "GitHub account", max_length=255, blank=True, null=True,
    )
    linkedin_account = models.URLField(
        "LinkedIn account", max_length=255, blank=True, null=True,
    )
    short_bio = models.CharField(
        "Describe yourself", max_length=60, blank=True, null=True,
    )
    bio = models.CharField(
        "Short biography", max_length=280, blank=True, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def get_profile_name(self):
        if self.name:
            return self.name

        return self.username
