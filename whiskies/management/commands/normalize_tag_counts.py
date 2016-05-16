from django.core.management import BaseCommand

from whiskies.command_functions import update_tagtracker_normalized_counts


class Command(BaseCommand):

    def handle(self, *args, **options):
        update_tagtracker_normalized_counts()
