from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    price = models.FloatField(null=False)
    image_url = models.URLField()
    category = models.CharField(max_length=100, default='No Category Listed')
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'


class Bid(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} bid {self.price} for {self.listing}'


class Comment(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    content = models.TextField(null=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} commented on {self.listing}'


class Watchlist(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('listing', 'user',)

    def __str__(self):
        return f'{self.user} watches {self.listing}'
