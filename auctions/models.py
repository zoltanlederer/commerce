from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class ActiveListing(models.Model):
    class Meta:
        verbose_name_plural = 'Active Listing'

    title = models.CharField(max_length=64)
    shortDescription = models.CharField(max_length=125)
    description = models.CharField(max_length=356)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.URLField(max_length=500, default='https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/495px-No-Image-Placeholder.svg.png')
    category = models.CharField(max_length=32)
    created = models.CharField(max_length=64, default='non')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class WatchList(models.Model):
    class Meta:
        verbose_name_plural = 'Watch list'

    user = models.CharField(max_length=64)
    items = models.ForeignKey(ActiveListing, on_delete=models.CASCADE)


class Comments(models.Model):
    class Meta:
        verbose_name_plural = 'Comments'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(ActiveListing, on_delete=models.CASCADE)
    comment = models.TextField(max_length=512, blank=True)
    created = models.DateTimeField(auto_now=True)


class Bids(models.Model):
    class Meta:
        verbose_name_plural = 'Bids'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(ActiveListing, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=7, decimal_places=2)
    created = models.DateTimeField(auto_now=True)
    