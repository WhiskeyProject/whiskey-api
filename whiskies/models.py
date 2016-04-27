from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        Profile.objects.create(user=instance)


class Whiskey(models.Model):
    title = models.CharField(max_length=255)
    img_url = models.URLField(null=True, blank=True)
    description = models.TextField()

    # These will be tied to live data in the future.
    price = models.IntegerField()
    rating = models.IntegerField()

    class Meta:
        default_related_name = "whiskies"


class Profile(models.Model):

    # https://docs.djangoproject.com/es/1.9/topics/db/examples/many_to_many/

    user = models.OneToOneField(User, null=True)

    liked_whiskies = models.ManyToManyField(Whiskey)
    disliked_whiskies = models.ManyToManyField(Whiskey)
    #searches = models.ManyToManyField(TagSearch)


class Review(models.Model):

    user = models.ForeignKey(User)
    whiskey = models.ForeignKey(Whiskey)
    text = models.TextField()
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        default_related_name = "reviews"


class TagSearch(models.Model):
    user = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag)

    class Meta:
        default_related_name = "tag_searches"


class Tag(models.Model):
    title = models.CharField(max_length=255)

    whiskies = models.ManyToManyField(Whiskey, through="TagTracker")

    class Meta:
        default_related_name = "tags"

    # overwrite save.
        # if not self.pk get or create tagtracker
        # call add_count
        # return rest of the save
    # overwrite delete
        # decrement tag tracker


class TagTracker(models.Model):
    count = 0

    whiskey = models.ForeignKey(Whiskey)
    tag = models.ForeignKey(Tag)

    def add_count(self):
        self.count += 1
