# from attendance business logic file
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List, Any # Added Dict, List, Any
from functools import reduce # Removed unused import operator
# from django.db.models import Q, F, Max # Removed unused imports
from tqdm import tqdm
# import gc # Removed unused import gc
from django.db import models, transaction
from django.db.models import Exists, OuterRef
from collections import deque
from django.utils import timezone
# from django.conf import settings # Removed unused import settings

from config.models import Shift
from resource.models import Employee, Logs, Attendance, ProcessedLogs, HolidayList, BiometricDeviceConfiguration
from value_config import WEEK_OFF_CONFIG # Assuming this is a dict like {'DEFAULT_WEEK_OFF': [6]}

import logging
import traceback # Keep for detailed error logging if needed

logger = logging.getLogger(__name__)

@dataclass
class ShiftWindow:
    name: str
    start_time: datetime
    end_time: datetime
    start_window: datetime
    end_window: datetime
    start_time_with_grace: datetime
    end_time_with_grace: datetime
    overtime_before_start: timedelta
    overtime_after_end: timedelta
    half_day_threshold: timedelta
    absent_threshold: timedelta  # Added for status calculation
    full_day_threshold: timedelta # Added for status calculation
    include_lunch_break_in_half_day: bool # Added for status calculation
    include_lunch_break_in_full_day: bool # Added for status calculation
    lunch_duration: timedelta # Added for status calculation

@dataclass
class ProcessedEmployee:
    """Dataclass to hold pre-processed employee info."""
    employee_obj: Employee
    first_weekoff: Optional[int]
    second_weekoff: Optional[int]
    join_date: Optional[datetime.date]
    leave_date: Optional[datetime.date]
    shift: Optional[Shift] # Store shift object directly

class AttendanceProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing AttendanceProcessor: Loading initial data...")

        # Use iterator() for potentially large querysets to reduce initial memory load
        self.all_shifts: List[Shift] = list(Shift.objects.iterator())
        self.shifts: Dict[Any, Shift] = {shift.pk: shift for shift in self.all_shifts} # Use PK for shift lookup
        self.shift_names: Dict[str, Shift] = {shift.name: shift for shift in self.all_shifts} # Keep name lookup for auto-shift

        self.employees: Dict[str, ProcessedEmployee] = self._load_employees()
        self.holidays: Dict[datetime.date, HolidayList] = {
            holiday.holiday_date: holiday for holiday in HolidayList.objects.iterator()
        }
        self.device_configs: Dict[Tuple[str, str], BiometricDeviceConfiguration] = {
            (device.device_no, device.serial_number): device
            for device in BiometricDeviceConfiguration.objects.iterator()
        }
        # Cache default week off days
        self.default_week_off: List[int] = WEEK_OFF_CONFIG.get('DEFAULT_WEEK_OFF', [])

        self.logger.info(
            f"Initialization complete. Loaded {len(self.all_shifts)} shifts, "
            f"{len(self.employees)} employees, {len(self.holidays)} holidays, "
            f"{len(self.device_configs)} device configs."
        )

    def _load_employees(self) -> Dict[str, ProcessedEmployee]:
        """Loads and pre-processes employee data."""
        employees_dict = {}
        for emp in Employee.objects.select_related('shift').iterator(): # Use select_related
            first_wo = None
            second_wo = None
            try:
                if emp.first_weekly_off is not None and emp.first_weekly_off != '':
                    first_wo = int(emp.first_weekly_off)
                if emp.second_weekly_off is not None and emp.second_weekly_off != '':
                    second_wo = int(emp.second_weekly_off)
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Invalid weekoff value for employee {emp.employee_id}: {e}. Skipping weekoff.")
            
            employees_dict[emp.employee_id] = ProcessedEmployee(
                employee_obj=emp,
                first_weekoff=first_wo,
                second_weekoff=second_wo,
                join_date=emp.date_of_joining,
                leave_date=emp.date_of_leaving,
                shift=emp.shift # Store the prefetched shift object
            )
        return employees_dict

    @transaction.atomic # Single transaction for the entire processing run
    def process_new_logs(self, batch_size: int = 5000) -> bool:
        """Process logs in batches and bulk-create ProcessedLogs entries per batch."""
        self.logger.info("Starting process_new_logs...")
        try:
            # Subquery to find unprocessed logs
            processed_ref = ProcessedLogs.objects.filter(id=OuterRef('id'))
            new_logs_qs = Logs.objects.annotate(
                is_processed=Exists(processed_ref)
            ).filter(is_processed=False).order_by('log_datetime')

            # Use iterator to avoid loading all logs at once
            log_iterator = new_logs_qs.iterator(chunk_size=batch_size) # Use chunk_size in iterator

            total_logs_estimated = new_logs_qs.count() # Estimate total for tqdm
            if total_logs_estimated == 0:
                self.logger.info("No new logs to process.")
                return True

            overall_success = True
            processed_count = 0

            with tqdm(total=total_logs_estimated, desc="Processing logs", unit="log", ncols=100) as pbar:
                while True:
                    current_batch_logs = list(next(log_iterator, [])) # Get next chunk
                    if not current_batch_logs:
                        break # No more logs

                    processed_in_batch_ids = set()
                    batch_success = True

                    # Removed per-log transaction, batch is processed sequentially
                    for log in current_batch_logs:
                        try:
                            # process_single_log now returns the log ID if successful, None otherwise
                            processed_log_id = self.process_single_log(log, is_manual=False)
                            if processed_log_id is not None:
                                processed_in_batch_ids.add(processed_log_id)
                            else:
                                batch_success = False # Mark batch as partially failed if any log fails
                                overall_success = False # Mark overall run as failed
                        except Exception as e:
                            self.logger.error(f"Critical error processing log {log.id} (Emp: {log.employeeid}): {str(e)}", exc_info=True)
                            # exc_info=True adds traceback to log
                            batch_success = False
                            overall_success = False
                        pbar.update(1)
                        processed_count += 1


                    # Bulk-create ProcessedLogs entries for successfully processed logs in this batch
                    if processed_in_batch_ids:
                        processed_entries = [
                            ProcessedLogs(id=log_id) # Only need the ID
                            for log_id in processed_in_batch_ids
                        ]
                        # Retry bulk create logic can be added here if needed
                        try:
                            ProcessedLogs.objects.bulk_create(processed_entries, ignore_conflicts=True) # ignore_conflicts is useful if retrying
                        except Exception as bulk_e:
                            self.logger.error(f"Error during bulk create of ProcessedLogs: {bulk_e}", exc_info=True)
                            overall_success = False # Mark run as failed if bulk create fails

                    # Optional: Add a small sleep or yield if this loop consumes too much CPU
                    # import time; time.sleep(0.01)

            self.logger.info(f"Finished process_new_logs. Processed {processed_count} logs.")
            return overall_success

        except Exception as e:
            self.logger.error(f"Fatal error in process_new_logs: {str(e)}", exc_info=True)
            return False # The atomic transaction will roll back


    def process_single_log(self, log: Logs, is_manual=False) -> Optional[int]:
        """
        Process a single attendance log.
        Returns the log ID if processing was successful, None otherwise.
        """
        if not log.employeeid:
            self.logger.warning(f"Log ID {log.id} has empty employee ID.")
            return None # Indicate failure

        employee_data = self.employees.get(log.employeeid)
        if not employee_data:
            self.logger.warning(f"Employee {log.employeeid} not found for log ID {log.id}.")
            return None # Indicate failure

        employee = employee_data.employee_obj
        log_date = log.log_datetime.date()

        # Check employee active period
        if ((employee_data.join_date and log_date < employee_data.join_date) or
                (employee_data.leave_date and log_date > employee_data.leave_date)):
            self.logger.debug(f"Log date {log_date} outside active period for employee {log.employeeid} (Log ID: {log.id}).")
            return None # Indicate failure (or should this be success but no action?) - Assuming failure for now.

        direction = None
        if is_manual:
            direction = log.direction.lower() if log.direction else None
        else:
            device_config = self.device_configs.get((log.shortname, log.serialno))
            if not device_config:
                self.logger.warning(f"Device config not found for log ID {log.id} (Device: {log.shortname}, SN: {log.serialno}).")
                return None # Indicate failure
            direction = device_config.direction_of_use.lower() if device_config.direction_of_use else None

        if not direction:
             self.logger.warning(f"Could not determine direction for log ID {log.id} (Emp: {log.employeeid}).")
             return None # Indicate failure

        # Simplify direction handling using a map or clearer if/elif
        handler = None
        fixed_shift = employee_data.shift is not None

        try:
            if direction == 'in':
                # Check if IN log is after an OUT log for the same day *before* calling handler
                # This query could be optimized if we cache attendance states per employee per day within a batch
                attendance_today = Attendance.objects.filter(
                    employeeid=employee,
                    logdate=log_date,
                    last_logtime__isnull=False # Check if an OUT punch exists
                ).only('pk').first() # only('pk') makes it slightly faster if we only need existence

                if attendance_today:
                    handler = self._handle_in_after_out
                elif fixed_shift:
                    handler = self._handle_in_log_fixedshift
                else:
                    handler = self._handle_in_log_autoshift
            elif direction == 'out':
                handler = self._handle_out_log_fixedshift if fixed_shift else self._handle_out_log_autoshift
            elif direction == 'both':
                 handler = self._handle_inout_log # This handles both fixed and auto internally now
            else:
                self.logger.warning(f"Unknown direction '{direction}' for log ID {log.id}.")
                return None # Indicate failure

            if handler:
                # Pass ProcessedEmployee data to avoid fetching Employee again
                if handler(employee_data, log, is_manual):
                     return log.id # Indicate success by returning log ID
                else:
                     return None # Indicate failure
            else:
                 # Should not happen if logic above is correct, but added as safeguard
                 self.logger.error(f"No handler determined for log ID {log.id} direction '{direction}'.")
                 return None

        except Exception as e:
            self.logger.error(f"Error processing log ID {log.id} for employee {log.employeeid}: {str(e)}", exc_info=True)
            return None # Indicate failure


    # Helper methods now accept ProcessedEmployee instead of Employee
    # Type hint updated for employee_data

    def _handle_in_after_out(self, employee_data: ProcessedEmployee, log: Logs, is_manual: bool = False) -> bool:
        """Handle IN logs received after OUT logs for the same date."""
        employee = employee_data.employee_obj
        log_datetime = log.log_datetime
        log_date = log_datetime.date()

        try:
            # Use select_for_update to lock the row during the read-modify-write cycle
            attendance = Attendance.objects.select_for_update().filter(
                employeeid=employee,
                logdate=log_date
            ).first()

            if attendance and attendance.last_logtime:
                temp_last_logtime = attendance.last_logtime

                # Process the current IN log first
                in_handler = self._handle_in_log_fixedshift if employee_data.shift else self._handle_in_log_autoshift
                if not in_handler(employee_data, log, is_manual):
                    self.logger.warning(f"Failed to process IN part of in-after-out for Emp {employee.employee_id}, Date {log_date}")
                    return False # Propagate failure

                # Refetch the attendance record as it was modified by the IN handler
                # Use select_for_update again if strict consistency is needed, though the row *should* still be locked
                # by the outer transaction context if using PostgreSQL REPEATABLE READ or higher.
                # Sticking to select_for_update for explicit locking during this complex operation.
                attendance = Attendance.objects.select_for_update().get(pk=attendance.pk)

                # Reset fields affected by OUT calculation before reprocessing OUT
                attendance.last_logtime = None
                attendance.total_time = None
                attendance.early_exit = None
                attendance.overtime = None
                attendance.shift_status = 'MP' # Reset status, will be recalculated
                attendance.out_direction = None
                attendance.out_shortname = None
                attendance.save()

                # Create a temporary log object representing the previous OUT log
                # Note: direction here might not matter as much as the timestamp
                temp_out_log = Logs(
                    employeeid=employee.employee_id,
                    log_datetime=temp_last_logtime,
                    direction='Out Device', # Or derive from original attendance? Keep simple for now.
                    shortname=attendance.out_shortname, # Preserve original out device if possible
                    serialno=None # Serial number might not be stored/relevant here
                )

                out_handler = self._handle_out_log_fixedshift if employee_data.shift else self._handle_out_log_autoshift
                if not out_handler(employee_data, temp_out_log, is_manual=False): # Assuming original OUT was not manual? Needs clarification.
                    self.logger.warning(f"Failed to re-process OUT part of in-after-out for Emp {employee.employee_id}, Date {log_date}")
                    # Decide how to handle failure here - rollback or leave as is?
                    # For now, return False, letting the outer transaction handle rollback if needed.
                    return False

                return True
            else:
                # If no existing attendance or no last_logtime, treat as a regular IN log
                in_handler = self._handle_in_log_fixedshift if employee_data.shift else self._handle_in_log_autoshift
                return in_handler(employee_data, log, is_manual)

        except Attendance.DoesNotExist:
             self.logger.error(f"Attendance record disappeared during _handle_in_after_out for Emp {employee.employee_id}, Date {log_date}")
             return False
        except Exception as e:
            self.logger.error(f"Error in _handle_in_after_out for employee {employee.employee_id}: {str(e)}", exc_info=True)
            return False


    def _handle_in_log_autoshift(self, employee_data: ProcessedEmployee, log: Logs, is_manual: bool = False) -> bool:
        """Handle incoming attendance log for auto shift employees."""
        employee = employee_data.employee_obj
        log_datetime = log.log_datetime
        log_date = log_datetime.date()

        try:
            matched_shift = None
            target_shift_window = None

            # Find the matching shift for this IN punch
            for auto_shift in self.all_shifts:
                try:
                    # Pass log_date directly as base_date
                    shift_window = self._calculate_shift_window(auto_shift, log_datetime, log_date)

                    # Check if log falls within the valid IN window for this shift
                    if shift_window.start_window <= log_datetime <= shift_window.end_window:
                        matched_shift = auto_shift
                        target_shift_window = shift_window
                        break # Found the first matching shift
                except Exception as e:
                    self.logger.debug(f"Error calculating window for shift {auto_shift.name} on {log_date}: {e}")
                    continue # Try next shift

            if not matched_shift or not target_shift_window:
                self.logger.debug(f"No matching auto-shift window found for IN log Emp {employee.employee_id} at {log_datetime}")
                # Decide policy: create Orphan log or just ignore? Assuming ignore for now.
                return True # Return True as the log itself didn't cause an error, just no action needed

            # Determine the definitive date for the attendance record based on the shift window
            attendance_date = target_shift_window.start_time.date()

            # Use update_or_create for atomicity and simplicity
            attendance, created = Attendance.objects.update_or_create(
                employeeid=employee,
                logdate=attendance_date,
                defaults={
                    'shift': matched_shift.name,
                    # Only update first_logtime if it's earlier than existing or null
                    # This requires a conditional update or fetching first, update_or_create is simpler
                    # If a log exists, we only set these if first_logtime is currently null.
                    'first_logtime': log_datetime,
                    'in_direction': 'Manual' if is_manual else 'Machine',
                    'in_shortname': None if is_manual else log.shortname,
                    'shift_status': 'MP', # Initial status, might be updated by OUT log later
                    'late_entry': max(timedelta(), log_datetime - target_shift_window.start_time_with_grace) if log_datetime > target_shift_window.start_time_with_grace else None
                }
            )

            # If the record already existed and had a first_logtime, we don't want to overwrite it here
            # unless the new log is earlier. Let's refine this.
            if not created:
                # Record existed, check if we need to update first_logtime
                if attendance.first_logtime is None or log_datetime < attendance.first_logtime:
                    attendance.first_logtime = log_datetime
                    attendance.in_direction = 'Manual' if is_manual else 'Machine'
                    attendance.in_shortname = None if is_manual else log.shortname
                    attendance.shift = matched_shift.name # Ensure shift is set/updated
                    attendance.shift_status = 'MP' if attendance.last_logtime is None else attendance.shift_status # Keep status if OUT exists
                    attendance.late_entry = max(timedelta(), log_datetime - target_shift_window.start_time_with_grace) if log_datetime > target_shift_window.start_time_with_grace else None
                    attendance.save()
                # else: log is later than existing first_logtime, ignore this IN punch for first_logtime update

            return True

        except Exception as e:
            self.logger.error(f"Error in _handle_in_log_autoshift for employee {employee.employee_id}: {str(e)}", exc_info=True)
            return False


    def _handle_out_log_autoshift(self, employee_data: ProcessedEmployee, log: Logs, is_manual: bool = False) -> bool:
        """Handle outgoing attendance log for auto shift employees."""
        employee = employee_data.employee_obj
        log_datetime = log.log_datetime
        log_date = log_datetime.date()

        try:
            # Ensure log_datetime is timezone-aware (should be handled by Django settings/ORM ideally)
            if log_datetime.tzinfo is None or log_datetime.tzinfo.utcoffset(log_datetime) is None:
                 log_datetime = timezone.make_aware(log_datetime, timezone.get_current_timezone())

            # Find the potentially relevant attendance record(s)
            # Priority: Today's record without an OUT time yet, or with an earlier OUT time.
            # Secondary: Yesterday's record without an OUT time (for night shifts ending today).
            possible_dates = [log_date, log_date - timedelta(days=1)]
            attendance = None

            # Fetch potential candidates efficiently
            potential_attendance = Attendance.objects.filter(
                employeeid=employee,
                logdate__in=possible_dates,
                first_logtime__isnull=False # Must have an IN punch
            ).order_by('-logdate') # Prioritize today's record

            target_attendance = None
            best_match_shift_window = None
            matched_shift = None

            for att in potential_attendance:
                if not att.shift: # Skip if shift name is missing
                     continue

                shift_obj = self.shift_names.get(att.shift)
                if not shift_obj:
                    self.logger.warning(f"Shift '{att.shift}' not found for Emp {employee.employee_id} on {att.logdate}")
                    continue

                # Calculate the expected shift window based on the attendance date and assigned shift
                try:
                    # Base date for window calculation should be the attendance record's date
                    shift_window = self._calculate_shift_window(shift_obj, log_datetime, att.logdate)
                except Exception as e:
                    self.logger.debug(f"Error calculating window for shift {shift_obj.name} on {att.logdate} for OUT log: {e}")
                    continue

                # Check if the OUT log falls within a reasonable time *after* the shift window started
                # (e.g., within 24 hours of shift start?) - Define a reasonable timeframe.
                # A simple check: OUT log is after the IN log.
                if att.first_logtime and log_datetime > att.first_logtime:
                     # Check if this OUT log is later than any existing OUT log for this record
                     if att.last_logtime is None or log_datetime > att.last_logtime:
                         # This is a potential candidate
                         target_attendance = att
                         best_match_shift_window = shift_window
                         matched_shift = shift_obj
                         break # Found the most likely record (prioritized by date)

            if not target_attendance:
                 # If no suitable existing record, create/update a record for today (or yesterday?)
                 # Policy: Create an 'orphan' OUT record for today if no match found?
                 # Let's create/update for log_date, assuming it's most likely.
                 attendance, created = Attendance.objects.update_or_create(
                     employeeid=employee,
                     logdate=log_date,
                     defaults={
                         'last_logtime': log_datetime,
                         'shift': '', # Unknown shift
                         'out_direction': 'Manual' if is_manual else 'Machine',
                         'out_shortname': None if is_manual else log.shortname,
                         'shift_status': 'MP' # Missing Punch
                     }
                 )
                 # If created or updated an orphan OUT, we might need to handle it differently.
                 # For now, just record it and return success.
                 self.logger.debug(f"Created/updated orphan OUT record for Emp {employee.employee_id} on {log_date}")
                 return True # Log processed, even if resulting status is MP


            # We have a target_attendance record and its corresponding shift_window
            # Update the target record with the OUT time and recalculate status
            with transaction.atomic(): # Use atomic block for read-modify-write
                # Refetch with lock
                locked_attendance = Attendance.objects.select_for_update().get(pk=target_attendance.pk)

                # Check again to prevent race conditions (though less likely with select_for_update)
                if locked_attendance.last_logtime is None or log_datetime > locked_attendance.last_logtime:
                    locked_attendance.last_logtime = log_datetime
                    locked_attendance.out_direction = 'Manual' if is_manual else 'Machine'
                    locked_attendance.out_shortname = None if is_manual else log.shortname

                    # Recalculate based on the matched shift and window
                    self._update_attendance_metrics(employee_data, locked_attendance, matched_shift, best_match_shift_window)
                    locked_attendance.save()
                # else: a later OUT log was processed concurrently, ignore this one.

            return True

        except Attendance.DoesNotExist:
             self.logger.error(f"Attendance record disappeared during _handle_out_log_autoshift for Emp {employee.employee_id}")
             return False
        except Exception as e:
            self.logger.error(f"Error in _handle_out_log_autoshift for employee {employee.employee_id}: {str(e)}", exc_info=True)
            return False

    def _handle_in_log_fixedshift(self, employee_data: ProcessedEmployee, log: Logs, is_manual: bool = False) -> bool:
        """Handle incoming attendance log for fixed shift employees."""
        employee = employee_data.employee_obj
        log_datetime = log.log_datetime
        shift = employee_data.shift # Get shift object directly

        if not shift: # Should not happen if employee_data.shift is populated correctly
             self.logger.error(f"Fixed shift employee {employee.employee_id} has no shift object assigned.")
             return False

        try:
            # Determine the correct date for the shift instance (usually log_date)
            # Night shift logic for IN needs care - an IN early morning might belong to yesterday's shift instance.
            log_date = log_datetime.date()
            attendance_date = log_date

            # Calculate the shift window for the log's date
            shift_window = self._calculate_shift_window(shift, log_datetime, log_date)

            # For night shifts starting late (e.g., 22:00) and IN punch is early next day (e.g., 01:00)
            # the attendance record should likely be for the *previous* day.
            # If the log time is significantly before the calculated start_window's start_time
            # and the shift is a night shift, associate with the previous day.
            # Heuristic: If log time is before shift end time on the *next* day, and also before shift start time on *current* day
            # it might belong to previous day's shift. Let's simplify: Use the window calculation logic.
            # The `_calculate_shift_window` should handle the base date adjustment.

            # If the log falls *before* the start window of the calculated shift,
            # it might belong to the *previous* day's shift instance. Recalculate window for prev day.
            if log_datetime < shift_window.start_window and shift.is_night_shift():
                 prev_date = log_date - timedelta(days=1)
                 prev_shift_window = self._calculate_shift_window(shift, log_datetime, prev_date)
                 # Check if it fits the previous day's window
                 if prev_shift_window.start_window <= log_datetime <= prev_shift_window.end_window:
                      attendance_date = prev_date
                      shift_window = prev_shift_window # Use the previous day's window for calculation
                 # Else: it doesn't fit previous day either, stick with current day (might be very early punch)

            # Use update_or_create for atomicity
            attendance, created = Attendance.objects.update_or_create(
                employeeid=employee,
                logdate=attendance_date,
                defaults={
                    'shift': shift.name,
                    'first_logtime': log_datetime,
                    'in_direction': 'Manual' if is_manual else 'Machine',
                    'in_shortname': None if is_manual else log.shortname,
                    'shift_status': 'MP',
                    'late_entry': max(timedelta(), log_datetime - shift_window.start_time_with_grace) if log_datetime > shift_window.start_time_with_grace else None
                }
            )

            if not created:
                 # Record existed, update first_logtime only if new one is earlier or current is null
                 if attendance.first_logtime is None or log_datetime < attendance.first_logtime:
                     attendance.first_logtime = log_datetime
                     attendance.in_direction = 'Manual' if is_manual else 'Machine'
                     attendance.in_shortname = None if is_manual else log.shortname
                     attendance.shift = shift.name # Ensure correct shift name
                     attendance.shift_status = 'MP' if attendance.last_logtime is None else attendance.shift_status
                     attendance.late_entry = max(timedelta(), log_datetime - shift_window.start_time_with_grace) if log_datetime > shift_window.start_time_with_grace else None
                     attendance.save()

            return True

        except Exception as e:
            self.logger.error(f"Error in _handle_in_log_fixedshift for employee {employee.employee_id}: {str(e)}", exc_info=True)
            return False

    def _handle_out_log_fixedshift(self, employee_data: ProcessedEmployee, log: Logs, is_manual: bool = False) -> bool:
        """Handle outgoing attendance log for fixed shift employees."""
        employee = employee_data.employee_obj
        log_datetime = log.log_datetime
        shift = employee_data.shift # Get shift object directly

        if not shift:
            self.logger.error(f"Fixed shift employee {employee.employee_id} has no shift object assigned.")
            return False

        try:
             # Ensure log_datetime is timezone-aware
            if log_datetime.tzinfo is None or log_datetime.tzinfo.utcoffset(log_datetime) is None:
                 log_datetime = timezone.make_aware(log_datetime, timezone.get_current_timezone())

            log_date = log_datetime.date()

            # Determine the most likely attendance date this OUT log belongs to.
            # Check today and yesterday.
            possible_dates = [log_date, log_date - timedelta(days=1)]
            target_attendance = None

            # Fetch potential candidates
            potential_attendance = Attendance.objects.filter(
                employeeid=employee,
                logdate__in=possible_dates,
                shift=shift.name, # Match the fixed shift name
                first_logtime__isnull=False # Must have an IN punch
            ).order_by('-logdate') # Prioritize today

            # Find the best match: Record where OUT is null or earlier than current log
            for att in potential_attendance:
                 if att.first_logtime and log_datetime > att.first_logtime: # Basic check: OUT > IN
                     if att.last_logtime is None or log_datetime > att.last_logtime:
                         target_attendance = att
                         break # Found most likely candidate

            if not target_attendance:
                 # Create/update an orphan OUT record for log_date
                 attendance, created = Attendance.objects.update_or_create(
                     employeeid=employee,
                     logdate=log_date,
                     defaults={
                         'shift': shift.name, # Assign fixed shift name
                         'last_logtime': log_datetime,
                         'out_direction': 'Manual' if is_manual else 'Machine',
                         'out_shortname': None if is_manual else log.shortname,
                         'shift_status': 'MP' # Missing IN Punch
                     }
                 )
                 self.logger.debug(f"Created/updated orphan OUT record for fixed shift Emp {employee.employee_id} on {log_date}")
                 return True # Log processed

            # We have a target_attendance record to update
            with transaction.atomic():
                 locked_attendance = Attendance.objects.select_for_update().get(pk=target_attendance.pk)

                 if locked_attendance.last_logtime is None or log_datetime > locked_attendance.last_logtime:
                     locked_attendance.last_logtime = log_datetime
                     locked_attendance.out_direction = 'Manual' if is_manual else 'Machine'
                     locked_attendance.out_shortname = None if is_manual else log.shortname

                     # Calculate shift window based on the attendance record's date
                     shift_window = self._calculate_shift_window(shift, log_datetime, locked_attendance.logdate)

                     # Recalculate metrics
                     self._update_attendance_metrics(employee_data, locked_attendance, shift, shift_window)
                     locked_attendance.save()

            return True

        except Attendance.DoesNotExist:
             self.logger.error(f"Attendance record disappeared during _handle_out_log_fixedshift for Emp {employee.employee_id}")
             return False
        except Exception as e:
            self.logger.error(f"Error in _handle_out_log_fixedshift for employee {employee.employee_id}: {str(e)}", exc_info=True)
            return False


    def _handle_inout_log(self, employee_data: ProcessedEmployee, log: Logs, is_manual: bool = False) -> bool:
        """Handles logs from devices marked as 'both' direction."""
        employee = employee_data.employee_obj
        log_datetime = log.log_datetime

        # Determine if it's fixed or auto shift
        is_fixed_shift = employee_data.shift is not None
        shift = employee_data.shift # Will be None for auto-shift employees

        try:
            # --- Logic similar to combining IN and OUT handlers ---
            attendance_date = log_datetime.date()
            target_attendance = None
            matched_shift_obj = None
            target_shift_window = None

            if is_fixed_shift:
                matched_shift_obj = shift
                # Determine attendance date for fixed shift (handle potential night shift boundary)
                temp_window = self._calculate_shift_window(matched_shift_obj, log_datetime, attendance_date)
                if log_datetime < temp_window.start_window and matched_shift_obj.is_night_shift():
                    prev_date = attendance_date - timedelta(days=1)
                    prev_window = self._calculate_shift_window(matched_shift_obj, log_datetime, prev_date)
                    if prev_window.start_window <= log_datetime <= prev_window.end_window: # Check IN window for prev day
                        attendance_date = prev_date
                        target_shift_window = prev_window
                if not target_shift_window: # If not assigned above
                     target_shift_window = self._calculate_shift_window(matched_shift_obj, log_datetime, attendance_date)

            else: # Auto Shift
                # Find matching shift based on IN window
                for auto_shift in self.all_shifts:
                    try:
                        sw = self._calculate_shift_window(auto_shift, log_datetime, attendance_date)
                        if sw.start_window <= log_datetime <= sw.end_window:
                            matched_shift_obj = auto_shift
                            target_shift_window = sw
                            attendance_date = sw.start_time.date() # Auto shift date is determined by window
                            break
                    except Exception:
                        continue
                if not matched_shift_obj:
                     # Could also check if log fits *after* a shift window for OUT association?
                     # Simpler: If no IN match, treat as potential OUT for today/yesterday
                     self.logger.debug(f"InOut log {log.id} for auto-shift Emp {employee.employee_id} didn't match IN window. Treating as potential OUT.")
                     # We might need to query existing records here like in _handle_out_log_autoshift
                     # For now, attempt to create/update for log_date if no match.
                     pass # Let it proceed to update_or_create below, potentially creating orphan


            # --- Update or Create Attendance ---
            # Use atomic transaction for the read-modify-write operations
            with transaction.atomic():
                attendance, created = Attendance.objects.update_or_create(
                    employeeid=employee,
                    logdate=attendance_date,
                    defaults={
                        # Set default shift name, might be updated below if existing record had one
                        'shift': matched_shift_obj.name if matched_shift_obj else '',
                        # Initialize other fields, status will be calculated
                        'shift_status': 'MP'
                    }
                )

                # Lock the fetched/created record
                locked_attendance = Attendance.objects.select_for_update().get(pk=attendance.pk)

                # Determine if log is IN or OUT based on existing times
                is_in_punch = False
                is_out_punch = False

                if locked_attendance.first_logtime is None or log_datetime < locked_attendance.first_logtime:
                    is_in_punch = True
                if locked_attendance.first_logtime is not None and (locked_attendance.last_logtime is None or log_datetime > locked_attendance.last_logtime):
                   # Only consider as OUT if it's *after* the first log time
                   if log_datetime > locked_attendance.first_logtime:
                       is_out_punch = True

                # Update fields based on determination
                updated = False
                if is_in_punch:
                    locked_attendance.first_logtime = log_datetime
                    locked_attendance.in_direction = 'Manual' if is_manual else 'Machine'
                    locked_attendance.in_shortname = None if is_manual else log.shortname
                    if matched_shift_obj: # Set shift if we determined one
                         locked_attendance.shift = matched_shift_obj.name
                    updated = True

                # IMPORTANT: Update OUT *only if* it's later than the IN time (which might have just been updated)
                first_time = locked_attendance.first_logtime # Use the potentially updated IN time
                if first_time and log_datetime > first_time and (locked_attendance.last_logtime is None or log_datetime > locked_attendance.last_logtime):
                     is_out_punch = True # Re-evaluate based on potentially new first_logtime
                     locked_attendance.last_logtime = log_datetime
                     locked_attendance.out_direction = 'Manual' if is_manual else 'Machine'
                     locked_attendance.out_shortname = None if is_manual else log.shortname
                     if matched_shift_obj: # Ensure shift name consistency
                         locked_attendance.shift = matched_shift_obj.name
                     updated = True
                else:
                     # If it wasn't determined as an OUT punch (e.g., earlier than first log)
                     is_out_punch = False


                if not is_in_punch and not is_out_punch:
                     # Log didn't update anything (e.g., duplicate punch time?)
                     self.logger.debug(f"InOut log {log.id} for Emp {employee.employee_id} did not result in IN or OUT update.")
                     # Still return True as log processing didn't fail.
                     return True

                # --- Recalculate Metrics ---
                # Find the correct shift object if not already determined (e.g., if record existed)
                final_shift_obj = matched_shift_obj
                if not final_shift_obj and locked_attendance.shift:
                     final_shift_obj = self.shift_names.get(locked_attendance.shift)

                if final_shift_obj and locked_attendance.first_logtime and locked_attendance.last_logtime:
                     # Ensure we have the correct shift window for the attendance date
                     final_shift_window = self._calculate_shift_window(final_shift_obj, log_datetime, locked_attendance.logdate)
                     self._update_attendance_metrics(employee_data, locked_attendance, final_shift_obj, final_shift_window)
                elif final_shift_obj and locked_attendance.first_logtime and is_in_punch and not is_out_punch:
                     # Only IN punch updated, calculate Late Entry if applicable
                     final_shift_window = self._calculate_shift_window(final_shift_obj, locked_attendance.first_logtime, locked_attendance.logdate)
                     locked_attendance.late_entry = max(timedelta(), locked_attendance.first_logtime - final_shift_window.start_time_with_grace) if locked_attendance.first_logtime > final_shift_window.start_time_with_grace else None
                     locked_attendance.shift_status = 'MP' # Reset status as OUT is missing/not yet processed
                elif locked_attendance.first_logtime is None or locked_attendance.last_logtime is None:
                     # If either punch is missing, mark as Missing Punch
                     locked_attendance.shift_status = 'MP'
                     # Clear calculated fields that depend on both punches
                     locked_attendance.total_time = None
                     locked_attendance.overtime = None
                     locked_attendance.early_exit = None # Late entry might still be valid if IN exists


                if updated:
                    locked_attendance.save()

            return True

        except Attendance.DoesNotExist:
             self.logger.error(f"Attendance record disappeared during _handle_inout_log for Emp {employee.employee_id}")
             return False
        except Exception as e:
            self.logger.error(f"Error in _handle_inout_log for employee {employee.employee_id}: {str(e)}", exc_info=True)
            return False


    # Consolidated Shift Window Calculation
    def _calculate_shift_window(self, shift: Shift, log_datetime: datetime, base_date: datetime.date) -> ShiftWindow:
        """
        Calculate shift time windows considering shift type, log time, and base date.
        Ensures timezone awareness.
        """
        # Ensure log_datetime is timezone-aware for calculations
        tzinfo = timezone.get_current_timezone() # Use project's default timezone
        if log_datetime.tzinfo is None or log_datetime.tzinfo.utcoffset(log_datetime) is None:
            aware_log_datetime = timezone.make_aware(log_datetime, tzinfo)
        else:
            aware_log_datetime = timezone.localtime(log_datetime, tzinfo) # Convert to project timezone if different

        # Make base_date timezone-aware datetime at the start of the day
        base_datetime_start = timezone.make_aware(datetime.combine(base_date, time.min), tzinfo)

        # Determine the effective date for the shift start based on log time and shift properties
        effective_date = base_date

        # Heuristic for night shifts: if log is early morning, it might belong to previous day's shift starting late.
        # Example: Shift 22:00-06:00. Log at 01:00 on Tue. Base date is Tue. Shift start should be Mon 22:00.
        # If shift starts late (e.g., >=18:00) and log time is early (e.g., < 08:00), consider previous day.
        is_potential_prev_day_log = (shift.is_night_shift() and
                                     shift.start_time >= time(18, 0) and
                                     aware_log_datetime.time() < time(8, 0))

        if is_potential_prev_day_log:
             # If log time is *before* the shift's end time calculated from the *previous* day's start,
             # then it belongs to the previous day's shift instance.
             prev_day_start_dt = timezone.make_aware(datetime.combine(base_date - timedelta(days=1), shift.start_time), tzinfo)
             prev_day_end_dt = prev_day_start_dt + shift.shift_duration # Approximate using duration if end time wraps? More reliable: calculate end time based on start + rules
             _calc_end_time = datetime.combine(
                prev_day_start_dt.date() + timedelta(days=1) if shift.is_night_shift() and shift.end_time < shift.start_time else prev_day_start_dt.date(),
                shift.end_time
             )
             prev_day_end_dt = timezone.make_aware(_calc_end_time, tzinfo)

             if aware_log_datetime < prev_day_end_dt:
                  effective_date = base_date - timedelta(days=1)


        # Create timezone-aware start and end times based on the effective date
        start_time = timezone.make_aware(datetime.combine(effective_date, shift.start_time), tzinfo)
        end_date = effective_date + timedelta(days=1) if shift.is_night_shift() and shift.end_time < shift.start_time else effective_date
        end_time = timezone.make_aware(datetime.combine(end_date, shift.end_time), tzinfo)

        # Calculate windows (ensure timedelta logic is correct)
        start_window = start_time - (shift.tolerance_before_start_time or timedelta())
        end_window = start_time + (shift.tolerance_after_start_time or timedelta())

        start_time_with_grace = start_time + (shift.grace_period_at_start_time or timedelta())
        end_time_with_grace = end_time - (shift.grace_period_at_end_time or timedelta())


        return ShiftWindow(
            name=shift.name,
            start_time=start_time,
            end_time=end_time,
            start_window=start_window,
            end_window=end_window,
            start_time_with_grace=start_time_with_grace,
            end_time_with_grace=end_time_with_grace,
            overtime_before_start=shift.overtime_threshold_before_start or timedelta(),
            overtime_after_end=shift.overtime_threshold_after_end or timedelta(),
            half_day_threshold=shift.half_day_threshold or timedelta.max, # Use max if None
            absent_threshold=shift.absent_threshold or timedelta(), # Use zero if None
            full_day_threshold=shift.full_day_threshold or timedelta(), # Use zero if None
            include_lunch_break_in_half_day=shift.include_lunch_break_in_half_day,
            include_lunch_break_in_full_day=shift.include_lunch_break_in_full_day,
            lunch_duration=shift.lunch_duration or timedelta()
        )


    # Consolidated Status/Metrics Calculation Helper
    def _update_attendance_metrics(self, employee_data: ProcessedEmployee, attendance: Attendance, shift: Shift, shift_window: ShiftWindow):
        """
        Recalculates total time, overtime, early/late status, and shift_status.
        Assumes attendance.first_logtime and attendance.last_logtime are set.
        Modifies the attendance object directly (but does not save).
        """
        if not attendance.first_logtime or not attendance.last_logtime:
             attendance.shift_status = 'MP' # Missing Punch
             attendance.total_time = None
             attendance.overtime = None
             attendance.early_exit = None
             # Late entry might be calculable if first_logtime exists
             if attendance.first_logtime:
                 attendance.late_entry = max(timedelta(), attendance.first_logtime - shift_window.start_time_with_grace) if attendance.first_logtime > shift_window.start_time_with_grace else None
             else:
                 attendance.late_entry = None
             return

        in_datetime = attendance.first_logtime
        out_datetime = attendance.last_logtime

        # Ensure timezone consistency (should ideally be handled before calling)
        tz = shift_window.start_time.tzinfo
        if in_datetime.tzinfo is None: in_datetime = timezone.make_aware(in_datetime, tz)
        if out_datetime.tzinfo is None: out_datetime = timezone.make_aware(out_datetime, tz)

        # --- Total Time ---
        total_time_raw = out_datetime - in_datetime
        lunch_deduction = timedelta()

        # Determine if lunch break should be deducted based on thresholds
        # Policy: Deduct if work duration (before deduction) meets or exceeds the relevant threshold?
        # Or deduct unconditionally if shift requires it? Let's assume deduction depends on achieved duration.
        # This logic might need refinement based on exact business rules.
        # Current Assumption: Deduct based on shift flags directly, if total time is positive.
        if total_time_raw > timedelta():
            # If EITHER flag is set, deduct lunch. (Or should it be based on calculated status?)
            # Simplest: If shift has lunch duration, deduct based on flags.
            # Refined: Deduct if full day threshold met and full day flag set, OR half day threshold met and half day flag set?
            # Let's stick to the original logic's apparent intent: Deduct if flag set.
            if shift_window.include_lunch_break_in_full_day or shift_window.include_lunch_break_in_half_day:
                 lunch_deduction = shift_window.lunch_duration

        total_time = total_time_raw - lunch_deduction
        attendance.total_time = total_time if total_time > timedelta() else timedelta() # Ensure non-negative

        # --- Late Entry / Early Exit ---
        attendance.late_entry = max(timedelta(), in_datetime - shift_window.start_time_with_grace) if in_datetime > shift_window.start_time_with_grace else None
        attendance.early_exit = max(timedelta(), shift_window.end_time_with_grace - out_datetime) if out_datetime < shift_window.end_time_with_grace else None

        # --- Overtime ---
        # Use shift_window times which are already timezone-aware
        overtime_threshold_before = shift_window.start_time - shift_window.overtime_before_start
        overtime_threshold_after = shift_window.end_time + shift_window.overtime_after_end

        overtime_before = max(timedelta(), overtime_threshold_before - in_datetime) if in_datetime < overtime_threshold_before else timedelta()
        overtime_after = max(timedelta(), out_datetime - overtime_threshold_after) if out_datetime > overtime_threshold_after else timedelta()
        calculated_overtime = overtime_before + overtime_after

        # --- Determine Week Off / Holiday ---
        is_holiday = attendance.logdate in self.holidays
        holiday_type = self.holidays[attendance.logdate].holiday_type if is_holiday else None

        # Get employee specific week offs, fallback to default
        weekoff_days = []
        if employee_data.first_weekoff is not None: weekoff_days.append(employee_data.first_weekoff)
        if employee_data.second_weekoff is not None: weekoff_days.append(employee_data.second_weekoff)
        if not weekoff_days: weekoff_days = self.default_week_off # Use cached default

        is_weekoff = attendance.logdate.weekday() in weekoff_days

        # --- Final Status and Overtime Assignment ---
        if is_holiday:
            if holiday_type == "PH":
                attendance.shift_status = 'PW' # Present on Public Holiday
            elif holiday_type == "FH":
                 attendance.shift_status = 'FW' # Present on Flexi/Floating Holiday
            else: # Default holiday handling if type is unknown
                 attendance.shift_status = 'PW'
            attendance.overtime = total_time_raw # On holiday/weekoff, all time might be considered OT (or based on policy) - Using raw time here
        elif is_weekoff:
            attendance.shift_status = 'WW' # Working on Week Off
            attendance.overtime = total_time_raw # All time is OT
        else:
            # Regular day status based on thresholds
            # Use the calculated total_time (after potential lunch deduction) for status check
            if total_time < shift_window.absent_threshold:
                attendance.shift_status = 'A'
            elif total_time < shift_window.half_day_threshold:
                attendance.shift_status = 'HD'
            elif total_time < shift_window.full_day_threshold:
                 # Assuming IH = Insufficient Hours (less than full day but more than half day)
                 # Requires a `full_day_threshold` to be defined in Shift model
                 attendance.shift_status = 'IH'
            else: # Meets or exceeds full day threshold
                 attendance.shift_status = 'P'

            # Assign calculated overtime only on regular workdays
            attendance.overtime = calculated_overtime if calculated_overtime > timedelta() else None

        # Handle edge case: If status ended up as 'A' but there are punches, maybe change to 'MP'?
        # Or keep 'A' if duration is below absent threshold? Let's keep 'A' as per logic.
        if attendance.shift_status != 'A' and attendance.shift_status != 'MP':
             if attendance.late_entry and attendance.early_exit:
                 attendance.shift_status += '-LE' # Append Late/Early markers if needed by downstream systems
             elif attendance.late_entry:
                 attendance.shift_status += '-L'
             elif attendance.early_exit:
                 attendance.shift_status += '-E'