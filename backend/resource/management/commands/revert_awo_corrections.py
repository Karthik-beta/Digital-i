import datetime
from django.core.management.base import BaseCommand
from resource.models import Attendance, AWOWorkOffCorrection
from tqdm import tqdm

class Command(BaseCommand):
    """
    Django management command to efficiently revert attendance records previously corrected
    from 'WO' (Week Off) to 'A' (Absent) due to the 'A-WO-A' pattern.

    **Purpose:**

    This command is designed to address scenarios where attendance records surrounding a
    previously corrected 'A-WO-A' pattern are updated, potentially invalidating the initial
    correction.

    The 'correct_a_wo_a_pattern' command identifies and resolves 'A-WO-A' patterns by
    changing the middle 'WO' day to 'A'.  However, if the 'A' statuses on either side of
    this corrected 'A' are later changed (e.g., updated to 'P' for Present due to late
    log entries or manual adjustments), the rationale for keeping the middle day as 'A'
    may no longer be valid.

    This command efficiently checks for these situations by querying a dedicated
    `AWOWorkOffCorrection` table, which stores records of all 'WO' to 'A' corrections made
    by the 'correct_a_wo_a_pattern' command. It then re-evaluates these corrections and
    reverts the 'A' status back to 'WO' if either the preceding or succeeding day's
    attendance is no longer 'A'.

    **Optimization and Efficiency:**

    This command is optimized for performance, especially when dealing with large attendance
    datasets and numerous corrections. Key optimizations include:

    *   **Targeted Querying:**  It directly queries the `AWOWorkOffCorrection` table, which contains
        only the records needing re-evaluation, instead of scanning the entire attendance dataset.
    *   **Prefetching:** Uses `prefetch_related('employee')` to minimize database queries when
        accessing employee information associated with correction records.
    *   **Efficient Data Fetching:**  Fetches attendance records only for the relevant three days
        (day before, corrected day, day after) for each correction record being processed.
    *   **Bulk Updates:** Employs `bulk_update` to efficiently update multiple attendance records
        in a single database operation when reverting statuses.
    *   **Progress Tracking:** Utilizes `tqdm` to provide a progress bar, allowing for monitoring
        of the command's execution, especially for long-running processes.
    *   **Cleanup:**  Deletes processed `AWOWorkOffCorrection` records after evaluation, ensuring
        that the table remains focused on active corrections and preventing redundant re-processing
        in subsequent runs.

    **Pre-requisites:**

    *   Ensure the `correct_a_wo_a_pattern` management command has been run at least once
        to populate the `AWOWorkOffCorrection` table.
    *   The `AWOWorkOffCorrection` model should be properly defined and migrated in your Django project.
    *   Database should be configured and accessible to the Django application.

    **Output:**

    The command provides informative output to the console, including:

    *   A success message indicating the start of the optimized A-WO-A reversal check.
    *   A progress bar showing the number of correction records being processed.
    *   Messages indicating the number of attendance records reverted back to 'WO' in bulk.
    *   Messages indicating the number of processed correction records deleted from the
        `AWOWorkOffCorrection` table.
    *   A summary message showing the total number of attendance records reverted and the
        completion of the command.

    **Important Notes:**

    *   This command is intended to be run periodically *after* any processes that might update
        historical attendance data, such as biometric data synchronization, manual corrections,
        or other attendance adjustments. Running it regularly helps maintain data consistency.
    *   The command assumes that the `AWOWorkOffCorrection` table accurately reflects the
        corrections made by the `correct_a_wo_a_pattern` command. Ensure that these commands
        are working in tandem as intended.
    *   It's recommended to schedule this command to run automatically (e.g., via cron job or
        Django-APScheduler) to ensure continuous monitoring and correction of attendance data.

    """
    help = 'Optimized: Reverts A-WO-A corrected records by querying correction table'

    def handle(self, *args, **options):
        """
        The main entry point for the `revert_awo_corrections` management command.

        This method orchestrates the process of reverting 'A-WO-A' corrections by:

        1.  Fetching all records from the `AWOWorkOffCorrection` table.
        2.  Iterating through each correction record, retrieving the relevant attendance data
            for the employee and the three days (day1, day2 - corrected day, day3).
        3.  Checking if the surrounding days (day1 and day3) are still 'A'. If not, and if
            day2 is still 'A' (meaning it was previously corrected), it reverts day2's status
            back to 'WO'.
        4.  Collecting attendance records that need to be updated and performing a bulk update
            for efficiency.
        5.  Deleting the processed `AWOWorkOffCorrection` records to clean up the table.
        6.  Providing console output to indicate progress and results.

        """
        updated_count = 0
        records_to_bulk_update = []
        corrections_to_delete = [] # To delete processed corrections

        self.stdout.write(self.style.SUCCESS("Starting optimized A-WO-A reversal check."))

        corrected_records = AWOWorkOffCorrection.objects.all().prefetch_related('employee') # Prefetch for efficiency

        with tqdm(total=corrected_records.count(), desc="Processing Corrected Records", unit="record", ncols=80) as pbar:
            for correction_record in corrected_records:
                day1 = correction_record.day1_date
                day2 = correction_record.corrected_date
                day3 = correction_record.day3_date
                employee = correction_record.employee

                # Efficiently fetch attendance for the 3 days for this employee
                employee_attendance = Attendance.objects.filter(
                    employeeid=employee,
                    logdate__in=[day1, day2, day3]
                ).order_by('logdate')
                attendance_map = {record.logdate: record for record in employee_attendance}

                if day1 in attendance_map and day2 in attendance_map and day3 in attendance_map:
                    day1_record = attendance_map[day1]
                    day2_record = attendance_map[day2]
                    day3_record = attendance_map[day3]

                    if day2_record.shift_status == 'A': # Still 'A' (meaning it was corrected)
                        if day1_record.shift_status != 'A' or day3_record.shift_status != 'A':
                            day2_record.shift_status = 'WO'
                            records_to_bulk_update.append(day2_record)
                            updated_count += 1
                            corrections_to_delete.append(correction_record) # Mark for deletion
                # else:
                #     corrections_to_delete.append(correction_record) # Mark for deletion if attendance record is missing

                pbar.update(1)

        if records_to_bulk_update:
            Attendance.objects.bulk_update(records_to_bulk_update, ['shift_status'])
            self.stdout.write(self.style.SUCCESS(f"Bulk reverted {len(records_to_bulk_update)} attendance records back to WO."))

        if corrections_to_delete:
            for correction in corrections_to_delete: # Delete in a loop for signals if any
                correction.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {len(corrections_to_delete)} processed correction records."))


        self.stdout.write(self.style.SUCCESS(f"Reverted {updated_count} attendance records from A back to WO (optimized)."))
        self.stdout.write(self.style.SUCCESS("Completed optimized A-WO-A reversal check."))