from django.core.management import BaseCommand

from whiskies.command_functions import update_whiskey_comps
from whiskies.models import Tag, Whiskey


class Command(BaseCommand):

    def handle(self, *args, **options):

        # loop through regions.
        tags = Tag.objects.all()
        whiskies = Whiskey.objects.all()

        update_whiskey_comps(whiskies, tags)


