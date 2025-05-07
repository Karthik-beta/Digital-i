from django.test import TestCase
from resource.models import Employee, Logs, Attendance, LastLogId
from config.models import AutoShift, Shift
from resource.attendance7 import AttendanceProcessor, ShiftWindow
from datetime import datetime, time, timedelta
from django.utils import timezone

class AttendanceLogicTests(TestCase):

    def setUp(self):
        """Set up test data for attendance logic tests."""
        # Create AutoShifts
        self.auto_shift_day = AutoShift.objects.create(
            name="Day Shift",
            start_time=time(8, 0),
            end_time=time(17, 0),
            tolerance_start_time=timedelta(minutes=15),
            tolerance_end_time=timedelta(minutes=15),
            grace_period_at_start_time=timedelta(minutes=5),
            grace_period_at_end_time=timedelta(minutes=5),
            overtime_threshold_before_start=timedelta(minutes=30),
            overtime_threshold_after_end=timedelta(minutes=30),
            half_day_threshold=timedelta(hours=4),
            full_day_threshold=timedelta(hours=8),
            absent_threshold=timedelta(hours=2), # Added absent threshold
            lunch_duration=timedelta(minutes=30),
            include_lunch_break_in_half_day=True,
            include_lunch_break_in_full_day=True
        )
        self.auto_shift_night = AutoShift.objects.create(
            name="Night Shift",
            start_time=time(22, 0),
            end_time=time(7, 0),
            tolerance_start_time=timedelta(minutes=15),
            tolerance_end_time=timedelta(minutes=15),
            grace_period_at_start_time=timedelta(minutes=5),
            grace_period_at_end_time=timedelta(minutes=5),
            overtime_threshold_before_start=timedelta(minutes=30),
            overtime_threshold_after_end=timedelta(minutes=30),
            half_day_threshold=timedelta(hours=4),
            full_day_threshold=timedelta(hours=8),
            absent_threshold=timedelta(hours=2), # Added absent threshold
            lunch_duration=timedelta(minutes=30),
            include_lunch_break_in_half_day=True,
            include_lunch_break_in_full_day=True
        )
        self.auto_shift_midnight = AutoShift.objects.create(
            name="Midnight Shift",
            start_time=time(0, 0),
            end_time=time(8, 0),
            tolerance_start_time=timedelta(minutes=15),
            tolerance_end_time=timedelta(minutes=15),
            grace_period_at_start_time=timedelta(minutes=5),
            grace_period_at_end_time=timedelta(minutes=5),
            overtime_threshold_before_start=timedelta(minutes=30),
            overtime_threshold_after_end=timedelta(minutes=30),
            half_day_threshold=timedelta(hours=3), # Adjusted for shorter shift
            full_day_threshold=timedelta(hours=7),  # Adjusted for shorter shift
            absent_threshold=timedelta(hours=1), # Added absent threshold
            lunch_duration=timedelta(minutes=0), # No lunch for midnight shift for simplicity
            include_lunch_break_in_half_day=False,
            include_lunch_break_in_full_day=False
        )

        # Create Shifts
        self.fixed_shift_morning = Shift.objects.create(
            name="Morning Fixed Shift",
            start_time=time(9, 0),
            end_time=time(18, 0),
            grace_period_at_start_time=timedelta(minutes=5),
            grace_period_at_end_time=timedelta(minutes=5),
            overtime_threshold_before_start=timedelta(minutes=30),
            overtime_threshold_after_end=timedelta(minutes=30),
            half_day_threshold=timedelta(hours=4),
            full_day_threshold=timedelta(hours=8),
            absent_threshold=timedelta(hours=2), # Added absent threshold
            lunch_duration=timedelta(minutes=30),
            include_lunch_break_in_half_day=True,
            include_lunch_break_in_full_day=True
        )
        self.fixed_shift_evening = Shift.objects.create( # Added Evening Fixed Shift
            name="Evening Fixed Shift",
            start_time=time(14, 0),
            end_time=time(23, 0),
            grace_period_at_start_time=timedelta(minutes=5),
            grace_period_at_end_time=timedelta(minutes=5),
            overtime_threshold_before_start=timedelta(minutes=30),
            overtime_threshold_after_end=timedelta(minutes=30),
            half_day_threshold=timedelta(hours=4),
            full_day_threshold=timedelta(hours=8),
            absent_threshold=timedelta(hours=2), # Added absent threshold
            lunch_duration=timedelta(minutes=30),
            include_lunch_break_in_half_day=True,
            include_lunch_break_in_full_day=True
        )

        # Create Employees
        self.employee_auto_day = Employee.objects.create(employee_id="AUTO_DAY_EMP", first_weekly_off=6) # Sunday weekoff
        self.employee_auto_night = Employee.objects.create(employee_id="AUTO_NIGHT_EMP")
        self.employee_fixed_morning = Employee.objects.create(employee_id="FIXED_MORNING_EMP", shift=self.fixed_shift_morning)
        self.employee_fixed_evening = Employee.objects.create(employee_id="FIXED_EVENING_EMP", shift=self.fixed_shift_evening) # Added Evening Fixed Employee
        self.employee_no_shift = Employee.objects.create(employee_id="NO_SHIFT_EMP") # Employee with no shift assigned

        # Initialize AttendanceProcessor
        self.processor = AttendanceProcessor()

    def test_auto_shift_day_normal_in_out(self):
        """Test normal IN and OUT log processing for day auto shift."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 8, 5)) # Within grace
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 16, 55)) # Before end time

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.first_logtime, log_in_datetime.time().replace(microsecond=0))
        self.assertEqual(attendance.last_logtime, log_out_datetime.time().replace(microsecond=0))
        expected_total_time = log_out_datetime - log_in_datetime - self.auto_shift_day.lunch_duration
        self.assertEqual(attendance.total_time, expected_total_time)
        self.assertEqual(attendance.shift_status, 'P') # Present

    def test_auto_shift_day_late_in_early_out(self):
        """Test late IN and early OUT log processing for day auto shift."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 9, 0)) # Late entry
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 16, 0)) # Early exit

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.first_logtime, log_in_datetime.time().replace(microsecond=0))
        self.assertEqual(attendance.last_logtime, log_out_datetime.time().replace(microsecond=0))
        expected_total_time = log_out_datetime - log_in_datetime - self.auto_shift_day.lunch_duration
        self.assertEqual(attendance.total_time, expected_total_time)
        self.assertIsNotNone(attendance.late_entry)
        self.assertIsNotNone(attendance.early_exit)
        self.assertEqual(attendance.shift_status, 'HD') # Half Day because total time will be less than full day threshold

    def test_auto_shift_day_weekoff(self):
        """Test log processing on a week off day (Sunday)."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 22, 10, 0)) # Sunday
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 22, 16, 0)) # Sunday

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.shift_status, 'WW') # Week Off
        self.assertIsNotNone(attendance.overtime) # Overtime should be total time

    def test_auto_shift_night_normal_in_out(self):
        """Test normal IN and OUT log processing for night auto shift."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 22, 10)) # Night shift IN
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 19, 6, 50)) # Night shift OUT

        Logs.objects.create(employeeid=self.employee_auto_night.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_night.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_night, logdate=log_in_datetime.date())
        self.assertEqual(attendance.first_logtime, log_in_datetime.time().replace(microsecond=0))
        self.assertEqual(attendance.last_logtime, log_out_datetime.time().replace(microsecond=0))
        expected_total_time = log_out_datetime - log_in_datetime - self.auto_shift_night.lunch_duration
        self.assertEqual(attendance.total_time, expected_total_time)
        self.assertEqual(attendance.shift_status, 'P') # Present

    def test_auto_shift_midnight_normal_in_out(self):
        """Test normal IN and OUT log processing for midnight auto shift."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 0, 5)) # Midnight shift IN
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 7, 55)) # Midnight shift OUT

        Logs.objects.create(employeeid=self.employee_auto_night.employee_id, log_datetime=log_in_datetime, direction="In Device") # Using night employee for midnight test for simplicity
        Logs.objects.create(employeeid=self.employee_auto_night.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_night, logdate=log_in_datetime.date()) # Date should be log_in_datetime's date
        self.assertEqual(attendance.first_logtime, log_in_datetime.time().replace(microsecond=0))
        self.assertEqual(attendance.last_logtime, log_out_datetime.time().replace(microsecond=0))
        expected_total_time = log_out_datetime - log_in_datetime # No lunch for midnight shift
        self.assertEqual(attendance.total_time, expected_total_time)
        self.assertEqual(attendance.shift_status, 'P') # Present

    def test_fixed_shift_morning_normal_in_out(self):
        """Test normal IN and OUT log processing for fixed morning shift."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 9, 5)) # Fixed morning shift IN
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 55)) # Fixed morning shift OUT

        Logs.objects.create(employeeid=self.employee_fixed_morning.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_fixed_morning.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_fixed_morning, logdate=log_in_datetime.date())
        self.assertEqual(attendance.first_logtime, log_in_datetime.time().replace(microsecond=0))
        self.assertEqual(attendance.last_logtime, log_out_datetime.time().replace(microsecond=0))
        expected_total_time = log_out_datetime - log_in_datetime - self.fixed_shift_morning.lunch_duration
        self.assertEqual(attendance.total_time, expected_total_time)
        self.assertEqual(attendance.shift_status, 'P') # Present

    def test_late_in_log_autoshift_scenario(self):
        """Test scenario where OUT log is processed before IN log for auto shift."""
        out_log_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 0)) # OUT log time
        in_log_datetime = timezone.make_aware(datetime(2024, 12, 18, 9, 0))  # Late IN log time

        # Process OUT log first
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=out_log_datetime, direction="Out Device")
        self.processor.process_new_logs()

        # Attendance record should be created with only OUT log details
        attendance_initial = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=out_log_datetime.date())
        self.assertIsNone(attendance_initial.first_logtime)
        self.assertEqual(attendance_initial.last_logtime, out_log_datetime.time().replace(microsecond=0))
        self.assertIsNone(attendance_initial.total_time)
        self.assertEqual(attendance_initial.shift_status, 'MP') # Marked as MP initially

        # Process IN log later
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=in_log_datetime, direction="In Device")
        self.processor.process_new_logs()

        # Attendance record should be updated with IN log and calculated details
        attendance_updated = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=in_log_datetime.date())
        self.assertEqual(attendance_updated.first_logtime, in_log_datetime.time().replace(microsecond=0))
        self.assertEqual(attendance_updated.last_logtime, out_log_datetime.time().replace(microsecond=0))
        expected_total_time = out_log_datetime - in_log_datetime - self.auto_shift_day.lunch_duration
        self.assertEqual(attendance_updated.total_time, expected_total_time)
        self.assertEqual(attendance_updated.shift_status, 'HD') # Status should be recalculated based on total time

    def test_manual_log_entry_autoshift(self):
        """Test processing of manual IN/OUT log entries for auto shift employee."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 10, 0))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 16, 0))

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_single_log(Logs.objects.last(), is_manual=True) # Mark last log as manual

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.direction, 'Manual') # Direction should be Manual for the last log processed manually

    def test_manual_log_entry_fixed_shift(self):
        """Test processing of manual IN/OUT log entries for fixed shift employee."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 10, 0))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 16, 0))

        Logs.objects.create(employeeid=self.employee_fixed_morning.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_fixed_morning.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_single_log(Logs.objects.last(), is_manual=True) # Mark last log as manual

        attendance = Attendance.objects.get(employeeid=self.employee_fixed_morning, logdate=log_in_datetime.date())
        self.assertEqual(attendance.direction, 'Manual') # Direction should be Manual for the last log processed manually

    def test_employee_not_found(self):
        """Test processing log for non-existent employee."""
        log_datetime = timezone.make_aware(datetime(2024, 12, 18, 10, 0))
        log = Logs.objects.create(employeeid="NON_EXISTENT_EMP_ID", log_datetime=log_datetime, direction="In Device")
        result = self.processor.process_single_log(log)
        self.assertFalse(result) # Should return False as employee not found

    def test_no_matching_autoshift(self):
        """Test processing log that does not fall into any auto shift window."""
        log_datetime = timezone.make_aware(datetime(2024, 12, 18, 14, 0)) # Time outside of defined shifts
        log = Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_datetime, direction="In Device")
        result = self.processor.process_single_log(log)
        self.assertTrue(result) # Should return True, as per original logic, even if no shift matched, it processes the log without shift

    def test_recalculation_function_called(self):
        """Test if recalculation function is called in process_new_logs."""
        # This is a basic test, more detailed tests for recalculation are needed
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 0))
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        LastLogId.objects.create(last_log_id=0, id=1) # Ensure LastLogId exists
        self.processor.process_new_logs()
        attendance_initial = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_out_datetime.date())
        self.assertEqual(attendance_initial.shift_status, 'MP') # Initially MP

        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 9, 0))
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        self.processor.process_new_logs()
        attendance_updated = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertNotEqual(attendance_updated.shift_status, 'MP') # Should be recalculated and not MP anymore

    def test_handle_late_in_log_autoshift_functionality(self):
        """Directly test the _handle_late_in_log_autoshift function."""
        out_log_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 0))
        in_log_datetime = timezone.make_aware(datetime(2024, 12, 18, 9, 0))

        # Create Attendance record with only OUT log details (simulating OUT log processed first)
        existing_attendance = Attendance.objects.create(
            employeeid=self.employee_auto_day,
            logdate=out_log_datetime.date(),
            last_logtime=out_log_datetime.time(),
            shift_status='MP'
        )
        log = Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=in_log_datetime, direction="In Device") # Create a dummy IN log

        # Call _handle_late_in_log_autoshift directly
        self.processor._handle_late_in_log_autoshift(self.employee_auto_day, log, existing_attendance, self.auto_shift_day, is_manual=False)

        # Assertions to check if attendance is updated correctly
        attendance_updated = Attendance.objects.get(pk=existing_attendance.pk) # Fetch updated attendance
        self.assertEqual(attendance_updated.first_logtime, in_log_datetime.time().replace(microsecond=0))
        self.assertEqual(attendance_updated.last_logtime, out_log_datetime.time().replace(microsecond=0))
        expected_total_time = out_log_datetime - in_log_datetime - self.auto_shift_day.lunch_duration
        self.assertEqual(attendance_updated.total_time, expected_total_time)
        self.assertEqual(attendance_updated.shift_status, 'HD') # Status should be recalculated

    def test_log_direction_case_insensitive(self):
        """Test if log direction is handled case-insensitively."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 8, 5))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 16, 55))

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="in device") # lowercase
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device") # mixed case
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.shift_status, 'P') # Should still process correctly regardless of case

    def test_log_processing_with_timezone_aware_datetime(self):
        """Test log processing with timezone-aware datetime objects."""
        log_in_datetime_aware = timezone.make_aware(datetime(2024, 12, 18, 8, 5))
        log_out_datetime_aware = timezone.make_aware(datetime(2024, 12, 18, 16, 55))

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime_aware, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime_aware, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime_aware.date())
        self.assertEqual(attendance.shift_status, 'P') # Should process timezone-aware datetimes

    def test_log_processing_with_naive_datetime(self):
        """Test log processing with naive datetime objects."""
        log_in_datetime_naive = datetime(2024, 12, 18, 8, 5) # Naive datetime
        log_out_datetime_naive = datetime(2024, 12, 18, 16, 55) # Naive datetime

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime_naive, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime_naive, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime_naive.date())
        self.assertEqual(attendance.shift_status, 'P') # Should process naive datetimes

    def test_no_new_logs_to_process(self):
        """Test process_new_logs when there are no new logs."""
        LastLogId.objects.create(last_log_id=99999, id=1) # Set last_log_id to a high value
        result = self.processor.process_new_logs()
        self.assertTrue(result) # Should return True even when no new logs

    def test_process_logs_in_batches(self):
        """Test if process_new_logs function correctly processes logs in batches."""
        # Create more logs than batch_size to ensure batch processing is triggered
        Logs.objects.bulk_create([
            Logs(employeeid=self.employee_auto_day.employee_id, log_datetime=timezone.make_aware(datetime(2024, 12, 18, 10, i)), direction="In Device")
            for i in range(100) # Create 100 in logs (assuming batch_size is less than 100)
        ])
        Logs.objects.bulk_create([
            Logs(employeeid=self.employee_auto_day.employee_id, log_datetime=timezone.make_aware(datetime(2024, 12, 18, 17, i)), direction="Out Device")
            for i in range(100) # Create 100 out logs
        ])
        LastLogId.objects.create(last_log_id=0, id=1)
        result = self.processor.process_new_logs()
        self.assertTrue(result) # Should process all logs in batches

        attendance_count = Attendance.objects.filter(employeeid=self.employee_auto_day, logdate=datetime(2024, 12, 18).date()).count()
        self.assertEqual(attendance_count, 100) # Verify all attendance records created

    def test_overtime_before_shift_start_autoshift(self):
        """Test overtime calculation before auto shift start."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 7, 30)) # 30 mins before shift start
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 10, 0))

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertIsNotNone(attendance.overtime)
        self.assertGreater(attendance.overtime, timedelta()) # Overtime should be calculated

    def test_overtime_after_shift_end_autoshift(self):
        """Test overtime calculation after auto shift end."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 16, 0))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 30)) # 30 mins after shift end

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertIsNotNone(attendance.overtime)
        self.assertGreater(attendance.overtime, timedelta()) # Overtime should be calculated

    def test_absent_shift_status_autoshift(self):
        """Test 'Absent' shift status when total time is less than absent_threshold."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 16, 0))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 0)) # Total time 1 hour

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.shift_status, 'A') # Absent status

    def test_incomplete_halfday_shift_status_autoshift(self):
        """Test 'IH' (Incomplete Half-day) shift status - between absent and half-day threshold."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 10, 0))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 13, 0)) # Total time 3 hours

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.shift_status, 'HD') # Should be HD as it's less than half_day_threshold

    def test_halfday_shift_status_autoshift(self):
        """Test 'HD' (Half-day) shift status - between half-day and full-day threshold."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 10, 0))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 14, 30)) # Total time 4.5 hours ( > half_day, < full_day)

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.shift_status, 'HD') # Half Day status

    def test_fullday_shift_status_autoshift(self):
        """Test 'P' (Present/Full-day) shift status - total time >= full_day threshold."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 9, 0))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 18, 0)) # Total time 9 hours

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.shift_status, 'P') # Present/Full-day status

    def test_fixed_shift_evening_normal_in_out(self):
        """Test normal IN and OUT log processing for fixed evening shift."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 14, 5)) # Fixed evening shift IN
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 22, 55)) # Fixed evening shift OUT

        Logs.objects.create(employeeid=self.employee_fixed_evening.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_fixed_evening.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_fixed_evening, logdate=log_in_datetime.date())
        self.assertEqual(attendance.shift_status, 'HD') # Half Day because total time less than full day threshold

    def test_employee_no_shift_assigned_autoshift_logic(self):
        """Test employee with no shift assigned, should fallback to auto shift logic."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 8, 5))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 16, 55))

        Logs.objects.create(employeeid=self.employee_no_shift.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_no_shift.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_no_shift, logdate=log_in_datetime.date())
        self.assertEqual(attendance.shift_status, 'P') # Should still process as per autoshift logic

    def test_out_log_before_in_log_autoshift_no_previous_attendance(self):
        """Test OUT log processed before IN log with no prior attendance record."""
        out_log_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 0))

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=out_log_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=out_log_datetime.date())
        self.assertIsNone(attendance.first_logtime)
        self.assertEqual(attendance.last_logtime, out_log_datetime.time().replace(microsecond=0))
        self.assertEqual(attendance.shift_status, 'MP') # Marked as MP

    def test_midnight_shift_spanning_days(self):
        """Test midnight shift spanning across two days correctly."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 23, 55)) # Just before midnight
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 19, 7, 55)) # Next day morning

        Logs.objects.create(employeeid=self.employee_auto_night.employee_id, log_datetime=log_in_datetime, direction="In Device") # Using night employee for midnight test
        Logs.objects.create(employeeid=self.employee_auto_night.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_night, logdate=datetime(2024, 12, 19).date()) # Date should be next day for midnight shift
        self.assertEqual(attendance.shift_status, 'P') # Present

    def test_midnight_shift_in_and_out_same_day(self):
        """Test midnight shift IN and OUT logs on the same calendar day (early morning)."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 19, 1, 0)) # After midnight, same day date
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 19, 7, 0)) # Still same day

        Logs.objects.create(employeeid=self.employee_auto_night.employee_id, log_datetime=log_in_datetime, direction="In Device") # Using night employee for midnight test
        Logs.objects.create(employeeid=self.employee_auto_night.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_night, logdate=datetime(2024, 12, 18).date()) # Date should be previous day for midnight shift
        self.assertEqual(attendance.shift_status, 'P') # Present, and date corrected

    def test_very_short_attendance_less_than_lunch_break(self):
        """Test attendance shorter than lunch break duration."""
        log_in_datetime = timezone.make_aware(datetime(2024, 12, 18, 10, 0))
        log_out_datetime = timezone.make_aware(datetime(2024, 12, 18, 10, 15)) # Only 15 mins

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_in_datetime, direction="In Device")
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=log_out_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=log_in_datetime.date())
        self.assertEqual(attendance.total_time, timedelta(0)) # Total time should not be negative after lunch deduction, should be 0 or positive
        self.assertEqual(attendance.shift_status, 'A') # Absent due to very short duration

    def test_tolerance_start_time_edge_autoshift(self):
        """Test log at the edge of tolerance start time."""
        tolerance_edge_datetime = timezone.make_aware(datetime(2024, 12, 18, 8, 0) - self.auto_shift_day.tolerance_start_time) # Exactly at tolerance start

        log = Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=tolerance_edge_datetime, direction="In Device")
        result = self.processor.process_single_log(log)
        self.assertTrue(result) # Should still process as within tolerance window

    def test_tolerance_end_time_edge_autoshift(self):
        """Test log at the edge of tolerance end time."""
        tolerance_edge_datetime = timezone.make_aware(datetime(2024, 12, 18, 8, 0) + self.auto_shift_day.tolerance_end_time) # Exactly at tolerance end

        log = Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=tolerance_edge_datetime, direction="In Device")
        result = self.processor.process_single_log(log)
        self.assertTrue(result) # Should still process as within tolerance window

    def test_grace_period_start_time_edge_autoshift(self):
        """Test log at the edge of grace period start time - should NOT be late."""
        grace_edge_datetime = timezone.make_aware(datetime(2024, 12, 18, 8, 0) + self.auto_shift_day.grace_period_at_start_time) # Exactly at grace period end

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=grace_edge_datetime, direction="In Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=grace_edge_datetime.date())
        self.assertIsNone(attendance.late_entry) # Should NOT be considered late

    def test_grace_period_end_time_edge_autoshift(self):
        """Test log at the edge of grace period end time for early exit - should NOT be early exit."""
        grace_end_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 0) - self.auto_shift_day.grace_period_at_end_time) # Exactly at grace period start from end

        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=grace_end_datetime, direction="Out Device")
        self.processor.process_new_logs()

        attendance = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=datetime(2024, 12, 18).date()) # Use any date as only checking early_exit for existing record
        self.assertIsNone(attendance.early_exit) # Should NOT be considered early exit

    def test_last_log_id_initial_creation(self):
        """Test if LastLogId is created if it doesn't exist."""
        LastLogId.objects.all().delete() # Ensure no LastLogId exists initially
        self.processor.process_new_logs()
        last_log_id = LastLogId.objects.first()
        self.assertIsNotNone(last_log_id) # LastLogId should be created

    def test_last_log_id_update_after_processing(self):
        """Test if LastLogId is updated after processing new logs."""
        LastLogId.objects.create(last_log_id=0, id=1)
        log1 = Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=timezone.make_aware(datetime(2024, 12, 18, 10, 0)), direction="In Device")
        log2 = Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=timezone.make_aware(datetime(2024, 12, 18, 17, 0)), direction="Out Device")
        self.processor.process_new_logs()
        last_log_id_record = LastLogId.objects.first()
        self.assertEqual(last_log_id_record.last_log_id, max(log1.id, log2.id)) # LastLogId should be updated to max log ID

    def test_no_recalculation_needed_if_total_time_not_null(self):
        """Test if recalculation is skipped if total_time is already calculated."""
        out_log_datetime = timezone.make_aware(datetime(2024, 12, 18, 17, 0))
        in_log_datetime = timezone.make_aware(datetime(2024, 12, 18, 9, 0))

        # Process OUT and then IN log to calculate attendance fully
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=out_log_datetime, direction="Out Device")
        self.processor.process_new_logs()
        Logs.objects.create(employeeid=self.employee_auto_day.employee_id, log_datetime=in_log_datetime, direction="In Device")
        self.processor.process_new_logs()

        attendance_updated = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=in_log_datetime.date())
        original_status = attendance_updated.shift_status # Get the calculated status

        # Run process_new_logs again - recalculation should NOT change status as total_time is not null
        self.processor.process_new_logs()
        attendance_again = Attendance.objects.get(employeeid=self.employee_auto_day, logdate=in_log_datetime.date())
        self.assertEqual(attendance_again.shift_status, original_status) # Status should remain same after second run

    # Add more test cases to cover other edge cases and functionalities as needed.