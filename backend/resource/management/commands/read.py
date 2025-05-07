import logging

# Set up logging
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand, CommandError
from resource.models import Logs  # Import your models
from resource.tasks import scan_for_data   # Import the function to execute

from datetime import timedelta

class Command(BaseCommand):
    help = 'Processes new logs from the database.'

    def handle(self, *args, **options):
        data = Logs.objects.all()
        for log in data:
            if Logs.objects.exists():
                logtime = log.log_datetime + timedelta(hours=5, minutes=30)
                self.stdout.write(self.style.SUCCESS(f"Successfully processed log {log.employeeid} .... {logtime}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Log {log.log_datetime} already exists in Logs2 table"))