from django.core.management.base import BaseCommand
from resource.models import Logs, ManualLogs, AllLogs
from django.db import transaction

BATCH_SIZE = 1000  # Define the batch size for database operations

class Command(BaseCommand):
    help = "Sync data from Logs and ManualLogs to AllLogs with minimal database hits"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting sync process for AllLogs...")
        
        # Sync Logs to AllLogs
        self.sync_logs_to_all_logs()
        
        # Sync ManualLogs to AllLogs
        self.sync_manual_logs_to_all_logs()
        
        self.stdout.write(self.style.SUCCESS("Sync process completed successfully."))

    def sync_logs_to_all_logs(self):
        """
        Sync data from Logs to AllLogs in batches.
        """
        self.stdout.write("Syncing Logs to AllLogs...")
        logs_queryset = Logs.objects.all().iterator(chunk_size=BATCH_SIZE)
        self.sync_to_all_logs(logs_queryset, source="Machine")

    def sync_manual_logs_to_all_logs(self):
        """
        Sync data from ManualLogs to AllLogs in batches.
        """
        self.stdout.write("Syncing ManualLogs to AllLogs...")
        manual_logs_queryset = ManualLogs.objects.all().iterator(chunk_size=BATCH_SIZE)
        self.sync_to_all_logs(manual_logs_queryset, source="Manual")

    def sync_to_all_logs(self, queryset, source):
        """
        Generic method to sync data to AllLogs from a given queryset.
        """
        batch = []
        existing_records = self.get_existing_all_logs()

        for record in queryset:
            # Prepare the data for AllLogs
            all_logs_data = {
                "employeeid": record.employeeid,
                "log_datetime": record.log_datetime,
                "direction": record.direction,
                "shortname": getattr(record, "shortname", None),
                "serialno": getattr(record, "serialno", None),
                "source": source,
            }

            # Check if the record already exists in AllLogs
            unique_key = (record.employeeid, record.log_datetime, record.direction, source)
            if unique_key not in existing_records:
                batch.append(AllLogs(**all_logs_data))
            else:
                # Update the existing record if the log_datetime is newer
                existing_record = existing_records[unique_key]
                if record.log_datetime > existing_record.log_datetime:
                    existing_record.employeeid = record.employeeid
                    existing_record.direction = record.direction
                    existing_record.shortname = getattr(record, "shortname", None)
                    existing_record.serialno = getattr(record, "serialno", None)
                    existing_record.log_datetime = record.log_datetime
                    existing_record.source = source
                    batch.append(existing_record)

            # Insert or update in batches
            if len(batch) >= BATCH_SIZE:
                self.bulk_save_all_logs(batch)
                batch = []

        # Save any remaining records
        if batch:
            self.bulk_save_all_logs(batch)

    def get_existing_all_logs(self):
        """
        Fetch all existing records from AllLogs and store them in a dictionary for quick lookup.
        """
        self.stdout.write("Fetching existing AllLogs records...")
        existing_records = {}
        all_logs_queryset = AllLogs.objects.all().iterator(chunk_size=BATCH_SIZE)
        for record in all_logs_queryset:
            unique_key = (record.employeeid, record.log_datetime, record.direction, record.source)
            existing_records[unique_key] = record
        return existing_records

    def bulk_save_all_logs(self, batch):
        """
        Perform a bulk save operation for a batch of AllLogs records.
        """
        new_records = [record for record in batch if record.id is None]  # New records without a primary key
        existing_records = [record for record in batch if record.id is not None]  # Existing records with a primary key

        with transaction.atomic():
            # Bulk create new records
            if new_records:
                AllLogs.objects.bulk_create(new_records, ignore_conflicts=True)

            # Bulk update existing records
            if existing_records:
                AllLogs.objects.bulk_update(
                    existing_records,
                    fields=["employeeid", "direction", "shortname", "serialno", "log_datetime", "source"],
                )

        self.stdout.write(f"Processed batch of {len(batch)} records (New: {len(new_records)}, Updated: {len(existing_records)}).")