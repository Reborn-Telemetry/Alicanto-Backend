import uuid
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    social_github = models.URLField(max_length=200, blank=True, null=True)
    social_linkedin = models.URLField(max_length=200, blank=True, null=True)
    social_twitter = models.URLField(max_length=200, blank=True, null=True)
    social_youtube = models.URLField(max_length=200, blank=True, null=True)
    social_website = models.URLField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    short_intro = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to='profiles/', default='profiles/user-default.png')

    def __str__(self):
        return str(self.user.username)
