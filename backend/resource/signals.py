from django.db.models.signals import post_save
from django.dispatch import receiver
from resource.models import Logs, ManualLogs, AllLogs
from typing import List, Tuple
import os
from dotenv import load_dotenv
from django.db.models.signals import post_migrate
from django.core.management import call_command

# Load the correct environment file
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

@receiver(post_migrate)
def initialize_data(sender, **kwargs):
    if ENVIRONMENT != 'local':
        try:
            call_command('reset_sequences')
            print("Sequences reset successfully.")
        except Exception as e:
            print(f"Failed to reset sequences: {e}")

        try:
            call_command('absentees', days=400)
            print("Absentees command executed successfully.")
        except Exception as e:
            print(f"Failed to execute absentees command: {e}")

        try:
            call_command('sync_logs')
            print("Sync logs command executed successfully.")
        except Exception as e:
            print(f"Failed to execute sync logs command: {e}")

        try:
            call_command('sync_all_logs')
            print("Sync all logs command executed successfully.")
        except Exception as e:
            print(f"Failed to execute sync all logs command: {e}")

        try:
            call_command('task')
            print("Task command executed successfully.")
        except Exception as e:
            print(f"Failed to execute task command: {e}")

        try:
            call_command('correct_a_wo_a_pattern')
            print("Correct A WO A pattern command executed successfully.")
        except Exception as e:
            print(f"Failed to execute correct A WO A pattern command: {e}")

        try:
            call_command('revert_awo_corrections')
            print("Revert A WO corrections command executed successfully.")
        except Exception as e:
            print(f"Failed to execute revert A WO corrections command: {e}")

@receiver(post_save, sender=Logs)
def copy_logs_to_all_logs(sender, instance, created, **kwargs):
    """
    Signal to copy data from Logs to AllLogs when a new log is created or updated.
    """
    AllLogs.objects.update_or_create(
        employeeid=instance.employeeid,
        log_datetime=instance.log_datetime,
        defaults={
            'direction': instance.direction,
            'shortname': instance.shortname,
            'serialno': instance.serialno,
            'source': 'Machine'
        }
    )

@receiver(post_save, sender=ManualLogs)
def copy_manual_logs_to_all_logs(sender, instance, created, **kwargs):
    """
    Signal to copy data from ManualLogs to AllLogs when a new manual log is created or updated.
    """
    AllLogs.objects.update_or_create(
        employeeid=instance.employeeid,
        log_datetime=instance.log_datetime,
        defaults={
            'direction': instance.direction,
            'shortname': None,  # Manual logs may not have a shortname
            'serialno': None,   # Manual logs may not have a serial number
            'source': 'Manual'
        }
    )

def trigger_all_logs_update(records: List[Tuple]):
    """
    Manually trigger the logic to update AllLogs after raw SQL insertion.
    """
    for record in records:
        # Assuming the record tuple matches the fields in the Logs/ManualLogs model
        try:
            AllLogs.objects.update_or_create(
                employeeid=record[1],
                log_datetime=record[5],
                defaults={
                    'direction': record[2],
                    'shortname': record[3],
                    'serialno': record[4],
                    'source': 'Machine'
                }
            )
        except Exception as e:
            # logger.error(f"Error processing record {record}: {e}")
            continue