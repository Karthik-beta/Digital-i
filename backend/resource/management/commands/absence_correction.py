import datetime
from django.core.management.base import BaseCommand
from django.db.models import F, Min, Q
from resource.models import Attendance, Employee
from tqdm import tqdm  # Import TQDM for progress bar
from django.db import transaction

class Command(BaseCommand):
    """
    Django management command to identify and update attendance records exhibiting the 'A-WO-A' pattern
    across three consecutive days.

    This command searches for the pattern:
    Day 1: 'A' (Absent)
    Day 2: 'WO' (Week Off)
    Day 3: 'A' (Absent)

    For records up to yesterday from the earliest attendance record date in the database.
    When the pattern is found, the 'shift_status' for Day 2 (Week Off) is updated to 'A' (Absent).

    Performance is optimized using:
        - Database indexes on 'logdate' and 'employeeid, logdate'.
        - Batch updates for efficient database modifications.
        - Efficient data structures (dictionaries) for record lookup.
        - TQDM progress bar for monitoring execution progress.
        - Reduced database hits by fetching attendance records in batches per date range.
    """
    help = 'Identifies and updates attendance records with A-WO-A pattern from earliest date'

    def handle(self, *args, **options):
        """
        The main entry point for the management command.

        Retrieves attendance records from the earliest date to yesterday, identifies 'A-WO-A' patterns,
        and updates the middle day's status to 'A' when the pattern is found.

        Uses TQDM to display a progress bar during date iteration and optimizes database access.
        """
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        # Find the earliest logdate in the database to start processing from
        earliest_attendance = Attendance.objects.aggregate(Min('logdate'))
        earliest_logdate = earliest_attendance['logdate__min']

        if earliest_logdate is None:
            self.stdout.write(self.style.WARNING("No attendance records found in the database."))
            return

        current_date = earliest_logdate
        updated_count = 0
        total_employees_processed = 0
        records_to_bulk_update = []  # List to store records for bulk update

        self.stdout.write(self.style.SUCCESS(
            f"Starting A-WO-A pattern check from earliest date: {earliest_logdate} to {yesterday}"
        ))

        # Calculate total number of days to process for TQDM progress bar
        total_days = (yesterday - earliest_logdate).days + 1

        # Iterate through dates from the earliest log date to yesterday, using tqdm for progress bar
        with tqdm(total=total_days, desc="Processing Dates", unit="day", ncols=80) as pbar:
            date_iterator = self.date_range_generator(earliest_logdate, yesterday)
            for day1, day2, day3 in date_iterator:
                date_range = [day1, day2, day3]
                # self.stdout.write(self.style.SUCCESS(f"Checking A-WO-A pattern for dates: {date_range}"))

                # Fetch all attendance records for the current 3-day date range in a single query
                all_date_range_attendance = Attendance.objects.filter(logdate__in=date_range).order_by('employeeid', 'logdate')

                # Group attendance records by employee ID for efficient processing
                employee_attendance_map = {}
                for record in all_date_range_attendance:
                    if record.employeeid_id not in employee_attendance_map:
                        employee_attendance_map[record.employeeid_id] = {}
                    employee_attendance_map[record.employeeid_id][record.logdate] = record

                # Process each employee's attendance records for the current date range
                for employee_id in employee_attendance_map:
                    total_employees_processed += 1
                    employee_dates_attendance = employee_attendance_map[employee_id]

                    # Check if attendance records exist for all three days in the pattern for this employee
                    if day1 in employee_dates_attendance and day2 in employee_dates_attendance and day3 in employee_dates_attendance:
                        day1_record = employee_dates_attendance[day1]
                        day2_record = employee_dates_attendance[day2]
                        day3_record = employee_dates_attendance[day3]

                        # Identify A-WO-A pattern
                        if (day1_record.shift_status == 'A' and
                                day2_record.shift_status == 'WO' and
                                day3_record.shift_status == 'A'):
                            day2_record.shift_status = 'A'
                            records_to_bulk_update.append(day2_record)  # Add record to bulk update list
                            updated_count += 1
                            # self.stdout.write(self.style.WARNING(f"Pattern found: Updated shift_status for employee {employee_id} on {day2} from WO to A."))
                pbar.update(1) # Update progress bar after processing each date range

        # Perform bulk update for all identified records
        if records_to_bulk_update:
            Attendance.objects.bulk_update(records_to_bulk_update, ['shift_status'])
            self.stdout.write(self.style.SUCCESS(f"Bulk updated {len(records_to_bulk_update)} attendance records."))

        self.stdout.write(self.style.SUCCESS(f"Successfully processed employees from earliest date to yesterday."))
        self.stdout.write(self.style.SUCCESS(f"Total employees processed: {total_employees_processed}."))
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} attendance records with WO to A based on A-WO-A pattern."))
        self.stdout.write(self.style.SUCCESS("Completed A-WO-A pattern check."))

    def date_range_generator(self, start_date, end_date):
        """
        Generates a sequence of 3-day date ranges from start_date to end_date.

        For each date, it yields the date itself and the following two consecutive dates,
        representing a 3-day window.

        Args:
            start_date (datetime.date): The starting date for range generation.
            end_date (datetime.date): The ending date for range generation.

        Yields:
            tuple: A tuple containing three datetime.date objects representing a 3-day date range (day1, day2, day3).
                   The iteration stops when day3 exceeds the end_date.
        """
        current_date = start_date
        while current_date <= end_date:
            day1 = current_date
            day2 = current_date + datetime.timedelta(days=1)
            day3 = current_date + datetime.timedelta(days=2)
            if day3 > end_date:  # Stop if day3 is in the future (after end_date)
                break
            yield day1, day2, day3
            current_date += datetime.timedelta(days=1)  # Move to the next day as starting point for 3-day window