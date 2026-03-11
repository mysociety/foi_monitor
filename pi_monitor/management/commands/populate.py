from django.core.management.base import BaseCommand

from pi_monitor.populate import populate


class Command(BaseCommand):
    help = "Populate the database from CSV source data in resources/"

    def handle(self, *args, **options):
        populate()
        self.stdout.write(self.style.SUCCESS("Population complete."))
