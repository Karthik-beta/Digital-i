from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from resource.models import Attendance, Employee, HolidayList
from tqdm import tqdm
from typing import List, Dict, Set
from datetime import date, timedelta
from collections import defaultdict
from value_config import WEEK_OFF_CONFIG

class Command(BaseCommand):
    help = "Creates new fields in Attendance model and marks absent employees for a given number of days starting from today"
    BATCH_SIZE = 1000  # Number of records to create at once

    def add_arguments(self, parser):
        """Define command arguments."""
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days to process starting from today'
        )

    def get_dates_to_process(self, num_days: int) -> List[date]:
        """Generate list of dates to process."""
        today = timezone.now().date()
        return [today - timedelta(days=i) for i in range(num_days)]

    def fetch_existing_attendance(self, dates: List[date]) -> Dict[int, Set[date]]:
        """Fetch existing attendance records grouped by employee ID."""
        existing_records = defaultdict(set)
        queryset = Attendance.objects.filter(logdate__in=dates).values_list('employeeid_id', 'logdate')
        for employee_id, logdate in queryset:
            existing_records[employee_id].add(logdate)
        return existing_records

    def create_attendance_objects(self, employees: List[Employee], dates: List[date], existing_records: Dict[int, Set[date]], holiday_dict: Dict[date, str]):
        """Generate attendance objects for batch insertion."""
        attendance_objects = []

        # Fetch all holidays for the given date range
        holidays = HolidayList.objects.filter(holiday_date__in=dates)
        holiday_dict = {holiday.holiday_date: holiday.holiday_type for holiday in holidays}

        for employee in employees:
            join_date = employee.date_of_joining or dates[-1]
            leave_date = employee.date_of_leaving or dates[0]
            first_weekoff = employee.first_weekly_off
            if isinstance(first_weekoff, str):
                try:
                    first_weekoff = int(first_weekoff)
                except (ValueError, TypeError):
                    self.stdout.write(self.style.WARNING(f"Employee {employee.id} has invalid first_weekly_off: {employee.first_weekoff}. Skipping week-off logic for this employee."))
                    first_weekoff = None
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Employee {employee.id} has error parsing first_weekly_off {employee.first_weekoff}: {e}. Skipping week-off logic."))
                    first_weekoff = None
            
            second_weekoff = employee.second_weekly_off
            if isinstance(second_weekoff, str):
                try:
                    second_weekoff = int(second_weekoff)
                except (ValueError, TypeError):
                    self.stdout.write(self.style.WARNING(f"Employee {employee.id} has invalid second_weekly_off: {employee.second_weekly_off}. Skipping week-off logic for this employee."))
                    second_weekoff = None
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Employee {employee.id} has error parsing second_weekly_off {employee.second_weekly_off}: {e}. Skipping week-off logic."))
                    second_weekoff = None

            for process_date in dates:
                if process_date < join_date or process_date > leave_date:
                    continue

                # is_week_off = process_date.weekday() in WEEK_OFF_CONFIG['DEFAULT_WEEK_OFF']
                if first_weekoff is not None or second_weekoff is not None:
                    if first_weekoff is not None and process_date.weekday() == first_weekoff:
                        is_week_off = True
                    elif second_weekoff is not None and process_date.weekday() == second_weekoff:
                        is_week_off = True
                    else:
                        is_week_off = False
                else:
                    is_week_off = process_date.weekday() in WEEK_OFF_CONFIG['DEFAULT_WEEK_OFF']

                if process_date in existing_records.get(employee.id, set()):
                    continue

                shift_status = 'WO' if is_week_off else 'A'
                
                # Check if the current date is a holiday
                if process_date in holiday_dict:
                    shift_status = holiday_dict[process_date]

                attendance_objects.append(
                    Attendance(
                        employeeid=employee,
                        logdate=process_date,
                        shift_status=shift_status
                    )
                )

                if len(attendance_objects) >= self.BATCH_SIZE:
                    yield attendance_objects
                    attendance_objects = []

        if attendance_objects:
            yield attendance_objects

    # @transaction.atomic
    # def handle(self, *args, **options):
    #     """Main command logic."""
    #     num_days = options['days']
    #     dates = self.get_dates_to_process(num_days)

    #     employees = Employee.objects.only('id', 'date_of_joining', 'date_of_leaving', 'first_weekly_off', 'second_weekly_off')  # Fetch only required fields
    #     if not employees.exists():
    #         self.stdout.write(self.style.WARNING("No employees found"))
    #         return

    #     existing_records = self.fetch_existing_attendance(dates)

    #     records_to_create = 0
    #     for employee in employees:
    #         join_date = employee.date_of_joining or dates[-1]
    #         leave_date = employee.date_of_leaving or dates[0]
    #         valid_dates = [date for date in dates if join_date <= date <= leave_date]
    #         existing_dates_for_employee = existing_records.get(employee.id, set())
    #         records_to_create += len(valid_dates) - len(existing_dates_for_employee)

    #     with tqdm(total=records_to_create, desc="Creating attendance records", unit="records") as pbar:
    #         for batch in self.create_attendance_objects(employees, dates, existing_records):
    #             Attendance.objects.bulk_create(batch)
    #             pbar.update(len(batch))

    #     self.stdout.write(
    #         self.style.SUCCESS(
    #             f"Successfully processed attendance for {num_days} days with {employees.count()} employees"
    #         )
    #     )

    @transaction.atomic
    def handle(self, *args, **options):
        """Main command logic."""
        num_days = options['days']
        # Get dates in reverse order (today, yesterday, ...)
        dates_to_process = self.get_dates_to_process(num_days)

        if not dates_to_process:
             self.stdout.write(self.style.WARNING("No dates to process."))
             return

        # Fetch all active employees
        employees = Employee.objects.only('id', 'date_of_joining', 'date_of_leaving', 'first_weekly_off', 'second_weekly_off').filter(
            Q(date_of_leaving__isnull=True) | Q(date_of_leaving__gte=dates_to_process[-1]) # Only employees whose leave date is null or after the earliest date we're checking
        ).filter(
             Q(date_of_joining__isnull=True) | Q(date_of_joining__lte=dates_to_process[0]) # Only employees whose join date is null or before the latest date we're checking
        ) 

        if not employees.exists():
            self.stdout.write(self.style.WARNING("No employees found matching the date criteria."))
            return

        self.stdout.write(f"Processing attendance for {employees.count()} employees over {num_days} days.")
        self.stdout.write(f"Dates to process: {min(dates_to_process)} to {max(dates_to_process)}")

        # Fetch existing attendance for the relevant dates
        existing_records = self.fetch_existing_attendance(dates_to_process)
        self.stdout.write(f"Found existing attendance records for {len(existing_records)} employees within the date range.")

        # Fetch all holidays for the given date range
        holidays = HolidayList.objects.filter(holiday_date__in=dates_to_process)
        holiday_dict = {holiday.holiday_date: holiday.holiday_type for holiday in holidays}
        self.stdout.write(f"Found {len(holidays)} holidays within the date range.")


        # Estimate total records to attempt creation for tqdm progress bar
        # This is an estimate *before* considering existing records and joins/leaves precisely
        estimated_records_to_attempt = employees.count() * num_days
        self.stdout.write(f"Estimated records to attempt: {estimated_records_to_attempt}")


        # Pass holiday_dict to the generator
        generator = self.create_attendance_objects(
            employees=list(employees), # Convert queryset to list if you need to iterate multiple times or want in-memory list
            dates=dates_to_process,
            existing_records=existing_records,
            holiday_dict=holiday_dict # Pass the fetched holiday dictionary
        )

        total_created = 0
        # Use the generator to process batches
        with tqdm(total=estimated_records_to_attempt, desc="Creating attendance records", unit="records") as pbar:
            try:
                for batch in generator:
                    if not batch:
                        continue # Should not happen with the yield logic, but safe check

                    # Use ignore_conflicts=True to handle potential race conditions or re-runs
                    # This tells the database to skip inserting rows that violate the unique constraint
                    Attendance.objects.bulk_create(batch, ignore_conflicts=True)
                    total_created += len(batch) # Update progress based on attempted count
                    pbar.update(len(batch))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error during bulk creation: {e}"))
                raise 

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished processing attendance. Attempted to create {total_created} records."
            )
        )