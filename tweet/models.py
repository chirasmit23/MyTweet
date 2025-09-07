
from django.db import models
from django.contrib.auth.models import User
from django.utils import timesince
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=200)
    photo = models.ImageField(upload_to="photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def __str__(self):
        return f'{self.user.username} - {self.text[:10]}'
class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # timestamp

    def __str__(self):
        return f'Comment by {self.user.username}'

    @property
    def time_since_posted(self):
        return f"{timesince(self.created_at)} ago"  # e.g. "5 minutes ago"
class Like(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can like a given tweet only once at the DB level:contentReference[oaicite:6]{index=6}.
        unique_together = ('tweet', 'user')

    def __str__(self):
        return f'{self.user.username} liked tweet {self.tweet.id}'

class Dislike(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="dislikes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tweet', 'user')

    def __str__(self):
        return f'{self.user.username} disliked tweet {self.tweet.id}'
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    username = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username