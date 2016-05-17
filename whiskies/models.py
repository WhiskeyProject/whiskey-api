from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        Profile.objects.create(user=instance)


class Whiskey(models.Model):
    """
    comparable field is set with a command and contains the other whiskies
    most similar to it in the database.
    """
    title = models.CharField(max_length=255)
    img_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    price = models.IntegerField()
    rating = models.IntegerField()

    review_count = models.IntegerField(null=True, blank=True)

    comparable = models.ManyToManyField("self", symmetrical=False,
                                        related_name="comparables")

    created_at = models.DateTimeField(auto_now_add=True)

    # def tag_match(self, tag_list):
    #     amount = self.tagtracker_set.filter(tag__title__in=tag_list).aggregate(
    #         Sum("count"))['count__sum']
    #     if amount:
    #         return amount
    #     else:
    #         return 0

    def __str__(self):
        return self.title

    class Meta:
        default_related_name = "whiskies"


class Profile(models.Model):
    """
    Profile for a user. This tracks their liked and disliked whiskies.

    """

    user = models.OneToOneField(User, null=True)

    liked_whiskies = models.ManyToManyField(Whiskey,
                                            related_name="liked_whiskies")

    disliked_whiskies = models.ManyToManyField(Whiskey,
                                            related_name="disliked_whiskies")

    def update_likes(self, whiskey_id, opinion, action):
        """
        Method for adding/removing a like/dislike whiskey.
        """

        if action == "add":
            if opinion == "like":
                self.liked_whiskies.add(Whiskey.objects.get(pk=whiskey_id))
            elif opinion == "dislike":
                self.disliked_whiskies.add(Whiskey.objects.get(pk=whiskey_id))

        elif action == "remove":
            if opinion == "like":
                self.liked_whiskies.remove(Whiskey.objects.get(pk=whiskey_id))
            elif opinion == "dislike":
                self.disliked_whiskies.remove(
                    Whiskey.objects.get(pk=whiskey_id))

        self.save()


class Review(models.Model):
    """
    A user generated review that can be created from a whiskey detail page.
    """

    user = models.ForeignKey(User)
    whiskey = models.ForeignKey(Whiskey)
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        default_related_name = "reviews"


class Tag(models.Model):
    """
    A single attribute that can be applied to a Whiskey.
    """

    title = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=255, null=True, blank=True)

    whiskies = models.ManyToManyField(Whiskey, through="TagTracker")

    def __str__(self):
        return self.title


    class Meta:
        default_related_name = "tags"


class TagSearch(models.Model):
    """
    When a logged in user makes a tag search an object is created to save
    that search. If they do not provide a title a default one will be
    generated in save() based on the search.
    """

    title = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User)
    search_string = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.title:
            items = self.search_string.split(',')
            if len(items) <= 3:
                self.title = ", ".join(items)
            else:
                self.title = ", ".join(items[:3]) + "..."

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        default_related_name = "tag_searches"
        ordering = ["-created_at"]


class TagTracker(models.Model):
    """
    A join table for Tag and Whiskey objects.

    count parameter tracks how many times the tag has been applied to the
    whiskey.

    normalized_count is the number of times the tag is applied to the whiseky
    per 100 reviews.
    """

    count = models.IntegerField(default=0)
    normalized_count = models.IntegerField(null=True, blank=True)

    whiskey = models.ForeignKey(Whiskey)
    tag = models.ForeignKey(Tag)

    class Meta:
        index_together = [["whiskey", "tag"]]


    def add_count(self, amount=1):

        self.count += amount

    def __str__(self):
        return "{} on {} {} times".format(self.tag, self.whiskey, self.count)
