from django.core.management import BaseCommand

from whiskies.command_functions import update_whiskey_comps
from whiskies.models import Tag, Whiskey


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--number', default=False, dest='number', type=int)

    def handle(self, *args, **options):

        tags = Tag.objects.all()
        whiskies = Whiskey.objects.all()

        if options['number']:
            update_whiskey_comps(whiskies, tags, number_comps=options['number'])
        else:
            update_whiskey_comps(whiskies, tags)
