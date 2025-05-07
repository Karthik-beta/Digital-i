from django.core.management.base import BaseCommand
import logging
from resource.attendance import AttendanceProcessor

# Set up logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Processes new logs from the database.'

    def handle(self, *args, **options):
        # scan_for_data()
        processor = AttendanceProcessor()
        processor.process_new_logs()
        
        self.stdout.write(self.style.SUCCESS('Successfully processed logs.'))

