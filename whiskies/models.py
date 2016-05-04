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
    description = models.TextField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    # These will be tied to live data in the future.
    price = models.IntegerField()
    rating = models.IntegerField()

    comparable = models.ManyToManyField('self', symmetrical=False,
                                        related_name="comparables")

    created_at = models.DateTimeField(auto_now_add=True)

    def tag_match(self, tag_list):
        # Double check if tag_list will be pks, titles, or objects.

        total = 0
        for tracker in self.tagtracker_set.all():
            if tracker.tag.title in tag_list:
                total += tracker.count
        return total

    def __str__(self):
        return self.title

    class Meta:
        default_related_name = "whiskies"


class Profile(models.Model):

    # https://docs.djangoproject.com/es/1.9/topics/db/examples/many_to_many/

    user = models.OneToOneField(User, null=True)

    liked_whiskies = models.ManyToManyField(Whiskey,
                                            related_name="liked_whiskies")

    disliked_whiskies = models.ManyToManyField(Whiskey,
                                            related_name="disliked_whiskies")

    def update_likes(self, whiskey_id, opinion, action):

        if action == "add":
            if opinion == "like":
                self.liked_whiskies.add(Whiskey.objects.get(pk=whiskey_id))
            elif opinion == "dislike":
                self.disliked_whiskies.add(Whiskey.objects.get(pk=whiskey_id))

        elif action == "remove":
            if opinion == "like":
                self.liked_whiskies.remove(Whiskey.objects.get(pk=whiskey_id))
            elif opinion == "dislike":
                self.disliked_whiskies.remove(Whiskey.objects.get(pk=whiskey_id))

        self.save()


class Review(models.Model):

    user = models.ForeignKey(User)
    whiskey = models.ForeignKey(Whiskey)
    text = models.TextField()
    rating = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = "reviews"


class Tag(models.Model):

    title = models.CharField(max_length=255)

    whiskies = models.ManyToManyField(Whiskey, through="TagTracker")

    def __str__(self):
        return self.title


    class Meta:
        default_related_name = "tags"


    # overwrite save.
        # if not self.pk get or create tagtracker
        # call add_count
        # return rest of the save
    # overwrite delete
        # decrement tag tracker


class TagSearch(models.Model):

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


class TagTracker(models.Model):
    count = models.IntegerField(default=0)

    whiskey = models.ForeignKey(Whiskey)
    tag = models.ForeignKey(Tag)

    def add_count(self):
        self.count += 1

    def __str__(self):
        return "{} on {} {} times".format(self.tag, self.whiskey, self.count)
