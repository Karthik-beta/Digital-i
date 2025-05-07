from django.core.management.base import BaseCommand
import logging
from resource.mandays import ManDaysAttendanceProcessor

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Processes new logs from the database.'

    def handle(self, *args, **options):
        # process_attendance()
        processor = ManDaysAttendanceProcessor()
        processor.process_logs()
        self.stdout.write(self.style.SUCCESS('Successfully processed logs.'))
