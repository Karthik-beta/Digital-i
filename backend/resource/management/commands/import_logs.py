import csv
from django.core.management.base import BaseCommand
from resource.models import Logs
from datetime import datetime
from tqdm import tqdm  # Import tqdm for progress bar

class Command(BaseCommand):
    help = 'Import logs from a CSV file into the Logs model'

    def add_arguments(self, parser):
        # Allow user to pass the CSV file path as an argument
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            # Open the CSV file
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)

                # Wrap the CSV reader with tqdm to show progress bar
                rows = list(csvreader)  # Convert to list for length calculation
                for row in tqdm(rows, desc="Importing logs", unit="row", ncols=100):
                    # Skip rows with missing required fields or incorrect data
                    if not row['id'] or not row['employeeid']:
                        self.stdout.write(self.style.ERROR(f"Skipping row with missing required data: {row}"))
                        continue

                    # Convert log_datetime to the proper datetime format
                    try:
                        log_datetime = datetime.fromisoformat(row['log_datetime'])
                    except ValueError:
                        self.stdout.write(self.style.ERROR(f"Skipping row with invalid date format: {row}"))
                        continue
                    
                    # Create Log record
                    log = Logs(
                        id=row['id'],
                        employeeid=row['employeeid'],
                        log_datetime=log_datetime,
                        direction=row['direction'],
                        shortname=row['shortname'],
                        serialno=row['serialno']
                    )
                    log.save()

                self.stdout.write(self.style.SUCCESS('Logs successfully imported from CSV file.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File '{csv_file_path}' not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))