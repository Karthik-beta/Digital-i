from django.core.management.base import BaseCommand
from resource.models import Logs, ManualLogs, AllLogs
from django.db import transaction

BATCH_SIZE = 1000  # Define the batch size for database operations

class Command(BaseCommand):
    help = "Sync data from Logs and ManualLogs to AllLogs with minimal database hits"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting sync process for AllLogs...")
        
        # Fetch all existing records from AllLogs once
        self.existing_all_logs_map = self.get_existing_all_logs_map() 
        
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
        # Pass the pre-fetched existing records map
        self.sync_to_all_logs(logs_queryset, source="Machine", existing_records_map=self.existing_all_logs_map)

    def sync_manual_logs_to_all_logs(self):
        """
        Sync data from ManualLogs to AllLogs in batches.
        """
        self.stdout.write("Syncing ManualLogs to AllLogs...")
        
        # Debug statement to check if there are manual logs
        manual_logs_count = ManualLogs.objects.count()
        self.stdout.write(f"Found {manual_logs_count} manual logs to process")
        
        manual_logs_queryset = ManualLogs.objects.all().iterator(chunk_size=BATCH_SIZE)
        # Pass the pre-fetched existing records map
        self.sync_to_all_logs(manual_logs_queryset, source="Manual", existing_records_map=self.existing_all_logs_map)

    def sync_to_all_logs(self, queryset, source, existing_records_map):
        """
        Generic method to sync data to AllLogs from a given queryset.
        Uses the pre-fetched existing_records_map.
        """
        batch_for_saving = [] # Contains new AllLogs instances and modified existing AllLogs instances
        processed_count = 0
        new_count = 0
        skipped_count = 0

        for record in queryset: # record is from Logs or ManualLogs
            processed_count += 1
            
            # Debug info for this record
            # self.stdout.write(f"Processing {source} record: {record.employeeid}, {record.log_datetime}, {record.direction}")
            
            # Prepare the data for AllLogs from the source record
            # This data is used for creating new AllLogs entries
            all_logs_data_from_source = {
                "employeeid": record.employeeid,
                "log_datetime": record.log_datetime,
                "direction": record.direction,
                "shortname": getattr(record, "shortname", None),
                "serialno": getattr(record, "serialno", None),
                "source": source,
            }

            # Define the unique key based on the source record's data and the target source type
            unique_key = (
                record.employeeid,
                record.log_datetime,
                record.direction,
                source  # "Machine" or "Manual"
            )

            if unique_key not in existing_records_map:
                # This specific combination (employeeid, log_datetime, direction, source) does not exist in AllLogs.
                # Create a new AllLogs entry.
                # self.stdout.write(f"Creating new {source} record as it doesn't exist in AllLogs")
                new_count += 1
                batch_for_saving.append(AllLogs(**all_logs_data_from_source))
            else:
                # An AllLogs record with the same key (employeeid, log_datetime, direction, source) already exists.
                existing_all_log_entry = existing_records_map[unique_key] # This is an AllLogs model instance
                # self.stdout.write(f"Found existing record with ID: {existing_all_log_entry.id}")

                # Check if non-key fields (e.g., shortname, serialno) need updating.
                needs_update = False
                new_shortname = all_logs_data_from_source["shortname"]
                new_serialno = all_logs_data_from_source["serialno"]

                if existing_all_log_entry.shortname != new_shortname:
                    # self.stdout.write(f"Updating shortname from {existing_all_log_entry.shortname} to {new_shortname}")
                    existing_all_log_entry.shortname = new_shortname
                    needs_update = True
                
                if existing_all_log_entry.serialno != new_serialno:
                    # self.stdout.write(f"Updating serialno from {existing_all_log_entry.serialno} to {new_serialno}")
                    existing_all_log_entry.serialno = new_serialno
                    needs_update = True

                if needs_update:
                    batch_for_saving.append(existing_all_log_entry)
                else:
                    skipped_count += 1
                    # self.stdout.write(f"Skipping {source} record as no changes needed")

            # Process batch if it reaches BATCH_SIZE
            if len(batch_for_saving) >= BATCH_SIZE:
                self.bulk_save_all_logs(batch_for_saving)
                batch_for_saving = []

        # Save any remaining records in the batch
        if batch_for_saving:
            self.bulk_save_all_logs(batch_for_saving)
            
        # Summary at the end
        self.stdout.write(f"Processed {processed_count} {source} records. New: {new_count}, Skipped: {skipped_count}")

    # Renamed from get_existing_all_logs and ensures it's called once
    def get_existing_all_logs_map(self):
        """
        Fetch all existing records from AllLogs and store them in a dictionary for quick lookup.
        The key includes the source field.
        """
        self.stdout.write("Fetching existing AllLogs records map (once)...") # Updated log message
        existing_map = {}
        all_logs_queryset = AllLogs.objects.all().iterator(chunk_size=BATCH_SIZE)
        for record in all_logs_queryset: # record here is an AllLogs instance
            unique_key = (record.employeeid, record.log_datetime, record.direction, record.source)
            existing_map[unique_key] = record # Store the AllLogs object itself
        return existing_map

    def bulk_save_all_logs(self, batch):
        """
        Perform a bulk save operation for a batch of AllLogs records.
        """
        # Separate new records and existing records
        new_records = [record for record in batch if record.id is None]
        existing_records = [record for record in batch if record.id is not None]

        try:
            with transaction.atomic():
                # Bulk create new records - always create fresh instances without IDs
                if new_records:
                    # For all operations, use fresh instances to avoid any ID issues
                    fresh_records = []
                    for record in new_records:
                        fresh_records.append(AllLogs(
                            employeeid=record.employeeid,
                            log_datetime=record.log_datetime,
                            direction=record.direction,
                            shortname=record.shortname,
                            serialno=record.serialno,
                            source=record.source
                            # Explicitly NOT copying the ID - let Django handle it
                        ))
                    
                    # Use ignore_conflicts=True to skip any records that would cause unique constraint violations
                    created = AllLogs.objects.bulk_create(fresh_records, ignore_conflicts=True)
                    self.stdout.write(f"Bulk created {len(created)} records")

                # Bulk update existing records
                if existing_records:
                    updated_count = AllLogs.objects.bulk_update(
                        existing_records,
                        fields=["shortname", "serialno"],  # Only update non-key fields
                    )
                    self.stdout.write(f"Bulk updated {updated_count} records")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Transaction failed: {str(e)}"))
            
        # Verify that records were actually saved
        if new_records:
            # Check the first new record as a verification
            sample = new_records[0]
            try:
                verification = AllLogs.objects.filter(
                    employeeid=sample.employeeid,
                    log_datetime=sample.log_datetime,
                    direction=sample.direction,
                    source=sample.source
                ).first()
                
                if verification:
                    self.stdout.write(self.style.SUCCESS(f"Verification: Record found in database with ID: {verification.id}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Verification FAILED: Record not found in database after save"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error during verification: {str(e)}"))

        self.stdout.write(f"Processed batch of {len(batch)} records (New: {len(new_records)}, Updated: {len(existing_records)}).")