from django.db import transaction
from .models import Logs, LastLogId, Attendance
from datetime import datetime
import logging 
from celery import shared_task

# from resource.attendance import AttendanceCalculator
from resource.attendance import AttendanceService
from resource.attendance import process_attendance
from tqdm import tqdm

# Set up logging
logger = logging.getLogger(__name__)

# def process_logs(log_data):
#     """
#     Processes a list of log entries one by one, sending each log for processing only
#     if the previous log was processed successfully.
#     """
#     process_success = True  # Flag to track overall processing success

#     for log_entry in log_data:  # Iterate through each Logs object in the QuerySet
#         if process_success:
#             service = AttendanceService(
#                 log_entry.employeeid,  # Access attributes directly
#                 log_entry.log_datetime,
#                 log_entry.direction
#             )
#             success = service.process_attendance()

#             if not success:  # If processing failed, break the loop
#                 print(f"Error processing log for employee: {log_entry.employeeid}")
#                 transaction.set_rollback(True)  # Rollback the transaction
#                 process_success = False  # Set the flag to False indicating failure
#                 break  # Stop processing further logs

#             # Update LastLogId after each successful log processing
#             with transaction.atomic():
#                 # LastLogId.objects.update(last_log_id=log_entry.id)
#                 pass

#             print(f"Log processed for employee: {log_entry.direction} at {log_entry.log_datetime}")

#     print("Logs processed.", log_data.count())
#     return process_success  # Return the overall processing success flag

@shared_task
def process_logs(log_data):
    """
    Processes a list of log entries one by one, sending each log for processing only
    if the previous log was processed successfully.
    """
    process_success = True  # Flag to track overall processing success

    # print("Processing logs...", log_data)

    with tqdm(total=log_data.count(), desc="Processing Logs", unit="log") as pbar:
        for log_entry in log_data:  # Iterate through each Logs object in the QuerySet
            if process_success:
                try:
                    # Update LastLogId before processing each log entry
                    with transaction.atomic():
                        LastLogId.objects.update(last_log_id=log_entry.id)

                    success = process_attendance(
                        log_entry.employeeid,  # Access attributes directly
                        log_entry.log_datetime,
                        log_entry.direction
                    )

                    if not success:  # If processing failed, break the loop
                        # print(f"Error processing log for employee: {log_entry.employeeid}")
                        # transaction.set_rollback(True)  # Rollback the transaction
                        # process_success = False  # Set the flag to False indicating failure
                        # break  # Stop processing further logs
                        continue

                # Update LastLogId after each successful log processing
                
                    # Update the progress bar
                    pbar.update(1)
                
                # except Attendance.MultipleObjectsReturned:
                #     # Skip to the next log entry if multiple objects are found
                #     continue

                except Exception as e:
                    # Log the exception and continue to the next log entry
                    logger.error(f"Error processing log for employee: {log_entry.employeeid}. {e}")
                    continue

                # print(f"Log processed for employee: {log_entry.direction} at {log_entry.log_datetime}")

    # print("Logs processed.", log_data.count())
    return process_success  # Return the overall processing success flag

@shared_task
def scan_for_data():
    try:
        with transaction.atomic():
            # Retrieve the LastLogId record or handle the case where it doesn't exist
            last_log_id_record = LastLogId.objects.select_for_update().first()
            
            if last_log_id_record is None:
                # If no LastLogId record exists, create a new one with default value
                last_log_id_record = LastLogId.objects.create(last_log_id=0)
            
            last_processed_id = last_log_id_record.last_log_id

            # Fetch new logs with an ID greater than the last processed ID
            new_logs = Logs.objects.filter(id__gt=last_processed_id).order_by('log_datetime')

            if new_logs.exists():  # Check if there are any new logs
                # print(f"Found {new_logs.count()} new logs")
                # logger.info(f"Found {new_logs.count()} new logs")

                # Process logs one by one with success check
                all_logs_processed_successfully = process_logs(new_logs)
                if all_logs_processed_successfully:
                    # print("Successfully processed logs.")
                    logger.info("Successfully processed logs.")

            else:
                # print("No new logs found.")
                logger.info("No new logs found.")

    except LastLogId.DoesNotExist:
        # Handle the case where LastLogId does not exist
        LastLogId.objects.create(last_log_id=0)
        pass
