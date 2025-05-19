# from attendance business logic file
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List, Any
from functools import reduce
# import operator
# from django.db.models import Q, F, Max
from tqdm import tqdm
# import gc
from django.db import models, transaction
from django.db.models import Exists, OuterRef
from collections import deque
from django.utils import timezone
# from django.conf import settings # Import settings

from config.models import Shift
from resource.models import Employee, AllLogs, Attendance, ProcessedLogs, HolidayList, BiometricDeviceConfiguration
from value_config import WEEK_OFF_CONFIG

import logging
import traceback

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

class AttendanceProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.auto_shifts = list(Shift.objects.all())
        self.shifts = {shift.name: shift for shift in Shift.objects.all()}
        self.employees = {emp.employee_id: emp for emp in Employee.objects.all()}
        self.holidays = {holiday.holiday_date: holiday for holiday in HolidayList.objects.all()}
        self.device_configs = {(device.device_no, device.serial_number): device for device in BiometricDeviceConfiguration.objects.all()}

    @transaction.atomic
    def process_new_logs(self, batch_size: int = 5000) -> bool:
        """Process logs in batches and bulk-create ProcessedLogs entries per batch."""
        try:
            # Subquery to find unprocessed logs
            processed_ref = ProcessedLogs.objects.filter(id=OuterRef('id'))
            new_logs = AllLogs.objects.annotate(
                is_processed=Exists(processed_ref)
            ).filter(is_processed=False).order_by('log_datetime')

            source = new_logs.values_list('source', flat=True).distinct()

            if not new_logs.exists():
                return True

            log_queue = deque(new_logs.iterator())
            total_logs = len(log_queue)
            success = True

            with tqdm(total=total_logs, desc="Processing logs", unit="log", ncols=80) as pbar:
                while log_queue:
                    # Process logs in batches to limit memory usage
                    current_batch = []
                    for _ in range(min(batch_size, len(log_queue))):
                        current_batch.append(log_queue.popleft())

                    processed_batch = []
                    for log in current_batch:
                        try:
                            with transaction.atomic():  # Atomic per log
                                if log.source.lower() == 'manual':
                                    self.process_single_log(log, is_manual=True)
                                    # print(f"Processing manual log: {log.id}, Employee ID: {log.employeeid}, Log DateTime: {log.log_datetime}, Direction: {log.direction}, Shortname: {log.shortname}, Serialno: {log.serialno}, source: {log.source}")
                                    processed_batch.append(log)
                                else:
                                    self.process_single_log(log, is_manual=False)
                                    # print(f"Processing log: {log.id}, Employee ID: {log.employeeid}, Log DateTime: {log.log_datetime}, Direction: {log.direction}, Shortname: {log.shortname}, Serialno: {log.serialno}, source: {log.source}")
                                    processed_batch.append(log)
                                # if self.process_single_log(log, is_manual=False):
                                #     processed_batch.append(log)
                                # else:
                                #     success = False
                        except Exception as e:
                            # self.logger.error(f"Error processing log {log.id}: {str(e)}")
                            success = False
                        pbar.update(1)

                    # Bulk-create for this batch
                    if processed_batch:
                        for log in processed_batch:
                            ProcessedLogs.objects.get_or_create(
                                id=log.id,
                                defaults={
                                    'employeeid': log.employeeid,
                                    'log_datetime': log.log_datetime,
                                    'direction': log.direction,
                                    'shortname': log.shortname,
                                    'serialno': log.serialno
                                }
                            )

            return success

        except Exception as e:
            # self.logger.error(f"Error in process_new_logs: {str(e)}")
            return False

    def process_single_log(self, log: AllLogs, is_manual=False) -> bool:
        """Process a single attendance log."""
        if not log.employeeid:
            # self.logger.error("Empty employee ID in log")
            return False

        try:
            # employee = Employee.objects.get(employee_id=log.employeeid)
            employee = self.employees.get(log.employeeid)
            join_date = employee.date_of_joining 
            leave_date = employee.date_of_leaving
            # print(f"Join Date: {join_date}, Leave Date: {leave_date}")
        except Employee.DoesNotExist:
            # self.logger.error(f"Employee with ID: {log.employeeid} not found.")
            return False
        except Exception as e:
            # self.logger.error(f"Error fetching employee {log.employeeid}: {str(e)}")
            return False
        
        if not is_manual:
            try:
                # Fetch the BiometricDeviceConfiguration from the pre-loaded dictionary
                device_config = self.device_configs.get((log.shortname, log.serialno))
                if not device_config:
                    # Log the missing device configuration for debugging purposes
                    # self.logger.error(f"Device configuration not found for device_no: {log.shortname}, serial_number: {log.serialno}")
                    return False
                # Get the direction_of_use from the device configuration
                direction = device_config.direction_of_use.lower()
            except Exception:
                return False
            
        if is_manual:
            # Handle manual logs
            # print(f"Manual Log tt: {log.direction}")
            direction = log.direction.lower()

        try:
            log_date = log.log_datetime.date()

            if ((join_date and log_date < join_date) or (leave_date and log_date > leave_date)):
                # self.logger.error(f"Log date {log_date} is outside employee's active period.")
                return False

            else:
                if employee.shift:
                    # Handle case when employee is assigned to a fixed shift  
                    if is_manual:
                        if direction == 'both':
                            return self._handle_inout_log(employee, log, is_manual=True)
                        elif direction == 'in':
                            # print("Passed through fixed shift In Device Manual")
                            attendance = Attendance.objects.filter(
                                employeeid=employee,
                                logdate=log.log_datetime.date()
                                ).first()
                            if attendance and attendance.last_logtime:
                                return self._handle_in_after_out(employee, log, is_manual=True)
                            else:
                                return self._handle_in_log_fixedshift(employee, log, is_manual=True)
                        elif direction == 'out':
                            # print("Passed through fixed shift Out Device Manual")
                            return self._handle_out_log_fixedshift(employee, log, is_manual=True)
                    else:
                        if direction == 'both':
                            return self._handle_inout_log(employee, log, is_manual=False)
                        elif direction == 'in':
                            # print("Passed through fixed shift In Device Auto")
                            attendance = Attendance.objects.filter(
                                employeeid=employee,
                                logdate=log.log_datetime.date()
                                ).first()
                            if attendance and attendance.last_logtime:
                                return self._handle_in_after_out(employee, log, is_manual=False)
                            else:
                                return self._handle_in_log_fixedshift(employee, log, is_manual=False)
                        elif direction == 'out':
                            # print("Passed through fixed shift Out Device Auto")
                            return self._handle_out_log_fixedshift(employee, log, is_manual=False)  
                else:  
                    # Handle auto-shift processing  
                    if is_manual:
                        if direction == 'both':
                            return self._handle_inout_log(employee, log, is_manual=True)
                        elif direction == 'in':
                            # print("Passed through auto shift In Device Manual")
                            attendance = Attendance.objects.filter(
                                employeeid=employee,
                                logdate=log.log_datetime.date()
                                ).first()
                            # print(f"Out Attendance found: {attendance}")
                            if attendance and attendance.last_logtime:
                                return self._handle_in_after_out(employee, log, is_manual=True)
                            else:
                                return self._handle_in_log_autoshift(employee, log, is_manual=True)
                        elif direction == 'out':
                            # print("Passed through auto shift Out Device Manual")
                            return self._handle_out_log_autoshift(employee, log, is_manual=True)
                    else:
                        if direction == 'both':
                            return self._handle_inout_log(employee, log, is_manual=False)
                        elif direction == 'in':
                            # print("Passed through auto shift In Device Auto")
                            attendance = Attendance.objects.filter(
                                employeeid=employee,
                                logdate=log.log_datetime.date()
                                ).first()                         
                            if attendance and attendance.last_logtime is not None:
                                return self._handle_in_after_out(employee, log, is_manual=False)
                            else:
                                return self._handle_in_log_autoshift(employee, log, is_manual=False)  
                        elif direction == 'out':
                            # print("Passed through auto shift Out Device Auto")
                            return self._handle_out_log_autoshift(employee, log, is_manual=False)  
                return True

        except Exception as e:
            # self.logger.error(f"Error processing log for employee {log.employeeid}: {str(e)}")
            return False
        
    def _handle_in_after_out(self, employee: Employee, log: AllLogs, is_manual: bool = False) -> bool:
        """Handle IN logs received after OUT logs for the same date."""
        try:
            log_datetime = log.log_datetime

            log_time = log_datetime.time()
            log_date = log_datetime.date()

            # Retrieve the existing attendance record
            attendance = Attendance.objects.filter(
                employeeid=employee,
                logdate=log_date
            ).first()

            if attendance and attendance.last_logtime:
                # Store the existing last_logtime temporarily
                temp_last_logdate = attendance.logdate
                temp_last_logtime = attendance.last_logtime

                # Process the current IN log first
                if employee.shift is not None:
                    self._handle_in_log_fixedshift(employee, log, is_manual=is_manual)
                else:
                    self._handle_in_log_autoshift(employee, log, is_manual=is_manual)

                # Retrieve the updated attendance record
                attendance = Attendance.objects.filter(
                    employeeid=employee,
                    logdate=log_date
                ).first() #Refetch after processing the in LOG

                # Reset related fields before reprocessing OUT
                attendance.last_logtime = None
                attendance.total_time = None
                attendance.early_exit = None
                attendance.overtime = None
                attendance.save()
                

                # Create a temporary log object representing the previous OUT log
                temp_out_log = AllLogs(
                    employeeid=employee.employee_id,
                    log_datetime=temp_last_logtime,
                    direction='out'
                )

                # print(f"Temp Out Log: {temp_out_log}")

                if employee.shift is not None:
                    # Reprocess the temporary OUT log to recalculate values
                    self._handle_out_log_fixedshift(employee, temp_out_log, is_manual=is_manual)
                else:
                    self._handle_out_log_autoshift(employee, temp_out_log, is_manual=is_manual)

                return True

            else:
                # If no existing attendance or no last_logtime, treat as a regular IN log
                if employee.shift is not None:
                    return self._handle_in_log_fixedshift(employee, log, is_manual)
                else:
                    return self._handle_in_log_autoshift(employee, log, is_manual)

        except Exception as e:
            # self.logger.error(f"Error in _handle_in_after_out for employee {employee.employee_id}: {str(e)}")
            return False

    def _handle_in_log_autoshift(self, employee: Employee, log: AllLogs, is_manual: bool = False) -> bool:
        """Handle incoming attendance log."""
        try:
            log_datetime = log.log_datetime 
            base_date = log_datetime.date() - timedelta(days=1) if time(0, 0) <= log_datetime.time() <= time(1, 30) else log_datetime.date()

            # Find the matching shift for this IN punch
            for auto_shift in self.auto_shifts:
                try:
                    shift_window = self._calculate_autoshift_window(auto_shift, log_datetime, base_date)

                    if shift_window.start_window <= log_datetime <= shift_window.end_window:
                        with transaction.atomic():  # Use a nested atomic block
                            existing_attendance = Attendance.objects.select_for_update().filter(
                                employeeid=employee,
                                logdate=shift_window.start_time.date()
                            ).first()

                            if existing_attendance:
                                if existing_attendance.first_logtime is None:
                                    attendance = existing_attendance
                                    attendance.first_logtime = log_datetime 
                                    attendance.shift = auto_shift.name
                                    attendance.in_direction = 'Manual' if is_manual else 'Machine'
                                    attendance.in_shortname = None if is_manual else log.shortname
                                    attendance.shift_status = 'MP'
                                else:
                                    return True
                            else:
                                attendance = Attendance(
                                    employeeid = employee,
                                    logdate = shift_window.start_time.date(),
                                    first_logtime = log_datetime,
                                    shift = auto_shift.name,
                                    in_direction = 'Manual' if is_manual else 'Machine',
                                    shift_status = 'MP'
                                )

                            if log_datetime > shift_window.start_time_with_grace:
                                attendance.late_entry = log_datetime - shift_window.start_time

                            attendance.save()
                            return True

                except Exception as e:
                    # self.logger.error(f"Error processing shift {auto_shift.name} for employee {employee.employee_id} in _handle_in_log_autoshift: {str(e)}")
                    continue

            return True

        except Exception as e:
            # self.logger.exception(f"Error in _handle_in_log_autoshift for employee {employee.employee_id}: {str(e)}")
            return False

          
    def _handle_out_log_autoshift(self, employee: Employee, log: AllLogs, is_manual: bool = False) -> bool:
        """
        Handle outgoing attendance log.
        Updates the last OUT time of an existing attendance record or creates a new OUT log if no valid IN found.
        """
        try:
            log_datetime = log.log_datetime # log_datetime is already datetime object
            # print(f"Log DateTime: {log_datetime}, Log Date: {log_datetime.date()}, Timezone: {log_datetime.tzinfo}, Is Manual: {is_manual}")

            if log_datetime.tzinfo is None:
                # If log_datetime is naive, make it timezone-aware
                log_datetime = timezone.make_aware(log_datetime, timezone.get_current_timezone())
                # print(f"Log DateTime after timezone aware: {log_datetime}, Timezone: {log_datetime.tzinfo}")
            else:
                log_datetime = log.log_datetime
                # print(f"Log DateTime: {log_datetime}, Timezone: {log_datetime.tzinfo}")


            log_date = log_datetime.date()

            # First check if there are any earlier logs for this day
            attendance = Attendance.objects.filter(
                employeeid=employee,
                logdate=log_date,
                first_logtime__isnull=False
            ).first()

            # print(f"Attendance found: {attendance}")

            if attendance and attendance.first_logtime > log_datetime:
                prev_date = log_date - timedelta(days=1)
                attendance = Attendance.objects.filter(
                    employeeid=employee,
                    logdate=prev_date,
                    first_logtime__isnull=False,
                    # last_logtime__isnull=True  # Must not have an OUT punch already
                ).first()

            if not attendance:
                prev_date = log_date - timedelta(days=1)
                attendance = Attendance.objects.filter(
                    employeeid=employee,
                    logdate=prev_date,
                    first_logtime__isnull=False,
                ).first()

            if not attendance:
                try:
                    attendance, created = Attendance.objects.update_or_create(
                        employeeid=employee,
                        logdate=log_date,
                        defaults={
                            'last_logtime': log_datetime,
                            'shift': '',
                            'out_direction': 'Manual' if is_manual else 'Machine',
                            'out_shortname': None if is_manual else log.shortname,
                            'shift_status': 'MP'
                        }
                    )
                    if not created:
                        # Handle conflict resolution if the record already exists
                        if attendance.last_logtime != log_datetime:
                            # Update the conflicting record with the new data
                            attendance.last_logtime = log_datetime
                            attendance.out_direction = 'Manual' if is_manual else 'Machine'
                            attendance.out_shortname = None if is_manual else log.shortname
                            attendance.shift_status = 'MP'
                            attendance.save()
                except Exception as e:
                    logger.error(f"Conflict detected while updating or creating attendance: {str(e)}")
                    return False

            if not attendance:
                return True

            try:
                auto_shift = self.shifts.get(attendance.shift)
                # print(f"Auto Shift: {auto_shift}")
            except Shift.DoesNotExist:
                # print(f"Shift {attendance.shift} not found for employee {employee.employee_id}.")
                return False


            in_datetime = attendance.first_logtime
            out_datetime = log_datetime

            # print(f"IN: {in_datetime}, OUT: {out_datetime}, Log Date: {attendance.logdate}")

            if auto_shift.is_night_shift():
                if auto_shift.start_time > auto_shift.end_time:
                    shift_end = datetime.combine(
                        attendance.logdate + timedelta(days=1),
                        auto_shift.end_time
                    )
                else:
                    shift_end = datetime.combine(
                        attendance.logdate,
                        auto_shift.end_time
                    )
            else:
                shift_end = datetime.combine(
                    attendance.logdate,
                    auto_shift.end_time
                )

            shift = self._calculate_autoshift_window(auto_shift, log_datetime, attendance.logdate)
            # print(f"Shift: {shift.name}, Start: {shift.start_time}, End: {shift.end_time}, Log Date: {attendance.logdate}")

            first_weekoff = employee.first_weekly_off
            if isinstance(first_weekoff, str):
                try:
                    first_weekoff = int(first_weekoff)
                except ValueError:
                    raise ValueError
                
            second_weekoff = employee.second_weekly_off
            if isinstance(second_weekoff, str):
                try:
                    second_weekoff = int(second_weekoff)
                except ValueError:
                    raise ValueError
                
            # is_weekoff = first_weekoff
            absent_threshold = auto_shift.absent_threshold if auto_shift.absent_threshold else None
            half_day_threshold = auto_shift.half_day_threshold if auto_shift.half_day_threshold else None
            full_day_threshold = auto_shift.full_day_threshold if auto_shift.full_day_threshold else None


            if out_datetime > in_datetime:
                # print(f"IN is less than OUT: {in_datetime} < {out_datetime}")
                if not attendance.last_logtime or out_datetime > attendance.last_logtime:
                    attendance.last_logtime = log_datetime
                    attendance.out_direction = 'Manual' if is_manual else 'Machine'
                    # attendance.out_shortname = log.shortname if log.shortname is not None else None
                    attendance.out_shortname = None if is_manual else log.shortname

                    total_time = out_datetime - in_datetime
                    # print(f"Total Time: {total_time}")

                    # print(f"Auto Shift: {auto_shift}, Include Lunch Break in Half Day: {auto_shift.include_lunch_break_in_half_day}, Include Lunch Break in Full Day: {auto_shift.include_lunch_break_in_full_day}")

                    if auto_shift.include_lunch_break_in_half_day and total_time >= auto_shift.lunch_duration:
                        total_time -= auto_shift.lunch_duration
                        attendance.total_time = total_time
                        # print(f"Total Time after half day lunch deduction: {attendance.total_time}")
                    else:
                        if auto_shift.include_lunch_break_in_full_day and total_time >= auto_shift.lunch_duration:
                            total_time -= auto_shift.lunch_duration
                            attendance.total_time = total_time
                            # print(f"Total Time after full day lunch deduction: {attendance.total_time}")
                        else:
                            attendance.total_time = total_time

                    # print(f"grace period: {shift.end_time_with_grace}")

                    # Calculate early exit
                    if out_datetime < shift.end_time_with_grace:
                        attendance.early_exit = shift.end_time - out_datetime
                        # print(f"Early exit: {attendance.early_exit}")
                    else:
                        attendance.early_exit = None
                        # print("Early exit is None")

                    # if shift.end_time < shift.start_time:
                    #     shift.end_time = shift.end_time + timedelta(days=1)

                    # Overtime calculation
                    overtime_threshold_before = shift.start_time - auto_shift.overtime_threshold_before_start
                    if shift.end_time < shift.start_time:
                        overtime_threshold_after = shift.end_time + auto_shift.overtime_threshold_after_end + timedelta(days=1)
                        # print(f"End Time: {shift.end_time}, Overtime After: {auto_shift.overtime_threshold_after_end}")
                        # print(f"overtime_threshold after: {overtime_threshold_after}")
                    else:
                        overtime_threshold_after = shift.end_time + auto_shift.overtime_threshold_after_end

                    # print(f"Overtime Threshold Before: {overtime_threshold_before}, After: {overtime_threshold_after}")

                    overtime_before = max(timedelta(), shift.start_time - in_datetime) if in_datetime < overtime_threshold_before else timedelta()                    
                    overtime_after = max(timedelta(), out_datetime - shift.end_time) if out_datetime > overtime_threshold_after else timedelta()
                
                    # if overtime_before > timedelta() or overtime_after > timedelta():
                        # print(f"Overtime Before: {overtime_before}, In: {in_datetime} & {overtime_threshold_before}. Overtime After: {overtime_after}, Out: {out_datetime} & {overtime_threshold_after}")

                    # Update status based on thresholds
                    # weekoff_days = [is_weekoff] if is_weekoff is not None else WEEK_OFF_CONFIG.get('DEFAULT_WEEK_OFF', [])
                    weekoff_days = []

                    if first_weekoff is not None:
                        weekoff_days.append(first_weekoff)

                    if second_weekoff is not None:
                        weekoff_days.append(second_weekoff)
                    
                    # If no week off days were found, fall back to the default week off configuration
                    if not weekoff_days:
                        weekoff_days = WEEK_OFF_CONFIG.get('DEFAULT_WEEK_OFF', [])

                    if attendance.logdate.weekday() in weekoff_days:
                        attendance.overtime = total_time
                    else:                                            
                        attendance.overtime = overtime_before + overtime_after if (overtime_before + overtime_after) > timedelta() else None

                    if attendance.logdate in self.holidays:
                        holiday = self.holidays[attendance.logdate]  # Get the HolidayList object
                        if holiday.holiday_type == "PH":
                            attendance.shift_status = 'PW'
                        elif holiday.holiday_type == "FH":
                            attendance.shift_status = 'FW'
                    elif attendance.logdate.weekday() in weekoff_days:
                        attendance.shift_status = 'WW'
                    elif absent_threshold is not None and total_time < absent_threshold:
                        attendance.shift_status = 'A'
                    elif half_day_threshold is not None and total_time < half_day_threshold:
                        attendance.shift_status = 'HD'
                    elif full_day_threshold is not None and total_time < full_day_threshold:
                        attendance.shift_status = 'IH'
                    else:
                        attendance.shift_status = 'P' if total_time > full_day_threshold else ''

                    # print(f"Attendance Status: {attendance.shift_status}, Total Time: {attendance.total_time}, Overtime: {attendance.overtime}")

                    try:
                        attendance.save()
                    except Exception as save_e:
                        # logger.error(f"Error saving attendance: {save_e}, Traceback: {traceback.format_exc()}")
                        return False

            return True

        except Exception as e:
            return False


    def _calculate_autoshift_window(self, auto_shift: Shift, log_datetime: datetime, base_date: datetime) -> ShiftWindow:
        """Calculate shift time windows considering both date and time, ensuring timezone awareness."""
        try:
            tzinfo = log_datetime.tzinfo  # Get the timezone from log_datetime
            base_date = base_date
            log_time = log_datetime.time()

            name = auto_shift.name

            # Special handling for midnight shift (00:00 start time)
            if auto_shift.start_time == time(0, 0):
                if time(23, 0) <= log_time <= time(23, 59, 59):
                    base_date += timedelta(days=1)

            if auto_shift.end_time == time(0, 0):
                if time(0, 0) <= log_time <= time(8, 0):
                    # base_date -= timedelta(days=1)
                    base_date = base_date

            # Create timezone-aware start and end times
            start_time = datetime.combine(
                base_date,
                auto_shift.start_time
            ).replace(tzinfo=tzinfo)
            end_time = datetime.combine(
                base_date + timedelta(days=1) if auto_shift.is_night_shift() and auto_shift.end_time < auto_shift.start_time else base_date,
                auto_shift.end_time
            ).replace(tzinfo=tzinfo)

            # Ensure window times are also timezone-aware
            if auto_shift.start_time == time(0, 0):
                start_window = start_time - timedelta(hours=1)
            else:
                start_window = start_time - auto_shift.tolerance_before_start_time
            
            end_window = start_time + auto_shift.tolerance_after_start_time

            return ShiftWindow(
                name=name,
                start_time=start_time,
                end_time=end_time,
                start_window=start_window,
                end_window=end_window,
                start_time_with_grace=start_time + auto_shift.grace_period_at_start_time,
                end_time_with_grace=end_time - auto_shift.grace_period_at_end_time,
                overtime_before_start=auto_shift.overtime_threshold_before_start,
                overtime_after_end=auto_shift.overtime_threshold_after_end,
                half_day_threshold=auto_shift.half_day_threshold
            )
        except Exception as e:
            # print(f"Error in _calculate_autoshift_window: {str(e)}")
            raise

    def _handle_in_log_fixedshift(self, employee: Employee, log: AllLogs, is_manual: bool = False) -> bool:
        """Handle incoming attendance log for fixed shift employees."""
        try:
            log_datetime = log.log_datetime

            # Get the employee's fixed shift
            shift = self.shifts.get(employee.shift.id)
            if not shift:
                # self.logger.error(f"Shift not found for employee {employee.employee_id}")
                return False
            
            shift_date = log_datetime.date()

            try:
                with transaction.atomic():
                    existing_attendance = Attendance.objects.select_for_update().filter(
                        employeeid=employee,
                        logdate=shift_date
                    ).first()

                    if existing_attendance:
                        if existing_attendance.first_logtime is None:
                            attendance = existing_attendance
                            attendance.first_logtime = log_datetime
                            attendance.shift = shift.name
                            attendance.in_direction = 'Manual' if is_manual else 'Machine'
                            attendance.in_shortname = None if is_manual else log.shortname
                            attendance.shift_status = 'MP'
                        else:
                            return True
                    else:
                        attendance = Attendance(
                            employeeid=employee,
                            logdate=shift_date,
                            first_logtime=log_datetime,
                            shift=shift.name,
                            in_direction= 'Manual' if is_manual else 'Machine',
                            shift_status='MP'
                        )

                    # Calculate shift start time for the current date
                    shift_start = timezone.make_aware(
                        datetime.combine(shift_date, shift.start_time),
                        log_datetime.tzinfo  # Ensure it has the same timezone as log_datetime
                    )
                    # print(f"Shift Start: {shift_start}, Log Date: {shift_date}, TimeZone of shift: {shift_start.tzinfo}, Timezone of log_datetime: {log_datetime.tzinfo}")
                    shift_start_with_grace = shift_start + shift.grace_period_at_start_time

                    # Check for late entry
                    if log_datetime > shift_start_with_grace:
                        attendance.late_entry = log_datetime - shift_start

                    attendance.save()
                    return True

            except Exception as e:
                # self.logger.error(f"Database error while processing IN log for employee {employee.employee_id}: {str(e)}")
                raise

        except Exception as e:
            # self.logger.error(f"Error in _handle_in_log_fixedshift for employee {employee.employee_id}: {str(e)}")
            return False
        
    def _handle_out_log_fixedshift(self, employee: Employee, log: AllLogs, is_manual: bool = False) -> bool:
        """
        Handle outgoing attendance log for fixed shift employees.
        Updates the last OUT time of an existing attendance record or creates a new OUT log if no valid IN found.
        """
        try:
            log_datetime = log.log_datetime
            log_date = log_datetime.date()

            # Get the employee's fixed shift
            shift = self.shifts.get(employee.shift.id)
            if not shift:
                # self.logger.error(f"Shift not found for employee {employee.employee_id}")
                return False
            
            shift_start = timezone.make_aware(
                datetime.combine(log_date, shift.start_time),
                log_datetime.tzinfo  # Ensure it has the same timezone as log_datetime
            )

            # Determine the correct logdate and check for existing attendance
            if shift.is_night_shift():
                # For night shifts, the log might belong to the previous day's shift
                if log_datetime < shift_start:
                    # If log time is before shift start, it belongs to previous day
                    log_date = log_date - timedelta(days=1)

            # Check for existing attendance records
            existing_attendance = Attendance.objects.filter(
                employeeid=employee,
                logdate=log_date
            ).first()

            # Handle different scenarios
            if existing_attendance:
                # If an attendance record exists and has an IN time
                if existing_attendance.first_logtime:
                    # Update the OUT time if it's later or not set
                    if not existing_attendance.last_logtime or log_datetime > existing_attendance.last_logtime:
                        existing_attendance.last_logtime = log_datetime
                        existing_attendance.out_direction = 'Manual' if is_manual else 'Machine'
                        existing_attendance.out_shortname = None if is_manual else log.shortname

                        # Calculate total time
                        in_datetime = existing_attendance.first_logtime
                        out_datetime = log_datetime

                        # Adjust for night shifts crossing midnight
                        if shift.is_night_shift() and in_datetime > out_datetime:
                            in_datetime -= timedelta(days=1)

                        total_time = out_datetime - in_datetime

                        # Deduct lunch break if applicable
                        # if shift.include_lunch_break_in_half_day or shift.include_lunch_break_in_full_day:
                        #     if shift.lunch_duration:
                        #         total_time -= shift.lunch_duration

                        if shift.include_lunch_break_in_half_day and total_time >= shift.lunch_duration:
                            total_time -= shift.lunch_duration
                            existing_attendance.total_time = total_time
                            # print(f"Total Time after half day lunch deduction: {attendance.total_time}")
                        else:
                            if shift.include_lunch_break_in_full_day and total_time >= shift.lunch_duration:
                                total_time -= shift.lunch_duration
                                existing_attendance.total_time = total_time
                                # print(f"Total Time after full day lunch deduction: {attendance.total_time}")
                            else:
                                existing_attendance.total_time = total_time

                        # existing_attendance.total_time = total_time

                        # Calculate shift timing
                        shift_start = timezone.make_aware(
                            datetime.combine(in_datetime.date(), shift.start_time),
                            log_datetime.tzinfo  
                        )
                        shift_end = timezone.make_aware(
                            datetime.combine(out_datetime.date(), shift.end_time),
                            log_datetime.tzinfo  
                        )
                        shift_end_with_grace = shift_end - shift.grace_period_at_end_time

                        # Early exit calculation
                        if out_datetime < shift_end_with_grace:
                            existing_attendance.early_exit = shift_end - out_datetime
                        else:
                            existing_attendance.early_exit = None

                        # Overtime calculation
                        overtime_threshold_before = shift_start - shift.overtime_threshold_before_start
                        overtime_threshold_after = shift_end + shift.overtime_threshold_after_end

                        overtime_before = max(timedelta(), shift_start - in_datetime) if in_datetime < overtime_threshold_before else timedelta()
                        overtime_after = max(timedelta(), out_datetime - shift_end) if out_datetime > overtime_threshold_after else timedelta()

                        # Shift status determination
                        first_weekoff = employee.first_weekly_off
                        if isinstance(first_weekoff, str):
                            try:
                                first_weekoff = int(first_weekoff)
                            except ValueError:
                                raise ValueError
                            
                        second_weekoff = employee.second_weekly_off
                        if isinstance(second_weekoff, str):
                            try:
                                second_weekoff = int(second_weekoff)
                            except ValueError:
                                raise ValueError
                        # weekoff_days = [first_weekoff] if first_weekoff is not None else WEEK_OFF_CONFIG.get('DEFAULT_WEEK_OFF', [])

                        weekoff_days = []

                        if first_weekoff is not None:
                            weekoff_days.append(first_weekoff)

                        if second_weekoff is not None:
                            weekoff_days.append(second_weekoff)
                        
                        # If no week off days were found, fall back to the default week off configuration
                        if not weekoff_days:
                            weekoff_days = WEEK_OFF_CONFIG.get('DEFAULT_WEEK_OFF', [])
                            
                        if existing_attendance.logdate.weekday() in weekoff_days:
                            existing_attendance.overtime = total_time
                        else:                        
                            existing_attendance.overtime = overtime_before + overtime_after if (overtime_before + overtime_after) > timedelta() else None

                        if existing_attendance.logdate in self.holidays:
                            holiday = self.holidays[existing_attendance.logdate]  # Get the HolidayList object
                            if holiday.holiday_type == "PH":
                                existing_attendance.shift_status = 'PW'
                            elif holiday.holiday_type == "FH":
                                existing_attendance.shift_status = 'FW'
                        elif existing_attendance.logdate.weekday() in weekoff_days:
                            existing_attendance.shift_status = 'WW'
                        elif shift.absent_threshold is not None and total_time < shift.absent_threshold:
                            existing_attendance.shift_status = 'A'
                        elif shift.half_day_threshold is not None and total_time < shift.half_day_threshold:
                            existing_attendance.shift_status = 'HD'
                        elif shift.full_day_threshold is not None and total_time < shift.full_day_threshold:
                            existing_attendance.shift_status = 'IH'
                        else:
                            existing_attendance.shift_status = 'P'

                        existing_attendance.save()
                else:
                    # If no IN time, just update the OUT time
                    existing_attendance.last_logtime = log_datetime
                    existing_attendance.shift = shift.name
                    existing_attendance.out_direction = 'Manual' if is_manual else 'Machine'
                    existing_attendance.out_shortname = None if is_manual else log.shortname
                    existing_attendance.shift_status = 'MP'
                    existing_attendance.save()
            else:
                # Create a new attendance record with OUT time
                Attendance.objects.create(
                    employeeid = employee,
                    logdate = log_date,
                    last_logtime = log_datetime,
                    out_direction = 'Manual' if is_manual else 'Machine',
                    out_shortname = None if is_manual else log.shortname,
                    shift = shift.name,
                    shift_status = 'MP'
                )

            return True

        except Exception as e:
            # self.logger.error(f"Error in _handle_out_log_fixedshift for employee {employee.employee_id}: {str(e)}", exc_info=True)
            return False
        
    def _handle_inout_log(self, employee: Employee, log: AllLogs, is_manual: bool = False) -> bool:
        """Handle 'in/out' logs for fixed shifts, recalculating status even for new records."""
        try:
            log_datetime = log.log_datetime
            # print(f"Log DateTime: {log_datetime}, Employee ID: {employee.employee_id}")

            log_time = log_datetime.time()
            log_date = log_datetime.date()
            shift = self.shifts.get(employee.shift.name) if employee.shift else None
            shift_date = log_date
            
            if not shift:
                # print(f"Shift not found for employee {employee.employee_id}")
                for auto_shift in self.auto_shifts:
                    try:
                        shift_window = self._calculate_autoshift_window(auto_shift, log_datetime)
                        # print(f"Shift Window: {shift_window.name}, Start: {shift_window.start_window}, End: {shift_window.end_window}, Log Date: {log_date}, Log Time: {log_time}")

                        if shift_window.start_window <= log_datetime <= shift_window.end_window:
                            # print(f"Auto Shift: {auto_shift.name}, Log Date: {log_date}, Log Time: {log_time}, Timezone: {log_datetime.tzinfo}")
                            with transaction.atomic():
                                attendance = Attendance.objects.select_for_update().filter(
                                    employeeid=employee, 
                                    logdate=shift_date
                                ).first()

                                if attendance and attendance.first_logtime is None:
                                    # If attendance exists but no IN time, set IN time
                                    attendance.first_logtime = log_datetime
                                    attendance.shift = auto_shift.name
                                    attendance.in_direction = 'Manual' if is_manual else 'Machine'
                                    attendance.in_shortname = None if is_manual else log.shortname
                                    attendance.shift_status = 'MP'
                                    attendance.save()
                                    return True

                                if not attendance:
                                    # Create new attendance without hardcoded status
                                    attendance = Attendance(
                                        employeeid=employee,
                                        logdate=shift_date,
                                        first_logtime=log_datetime,
                                        last_logtime=None,
                                        shift=auto_shift.name,
                                        in_direction='Manual' if is_manual else 'Machine',
                                        in_shortname=None if is_manual else log.shortname,
                                        shift_status='MP'
                                    )
                                    attendance.save()  # Save first to generate ID

                                    update_needed = False

                                # Update first/last logtimes if needed
                                if (attendance.first_logtime is None or log_datetime < attendance.first_logtime):
                                    attendance.first_logtime = log_datetime
                                    update_needed = True
                                if (attendance.last_logtime is None or (log_datetime > attendance.last_logtime and log_datetime > attendance.first_logtime)):
                                    attendance.last_logtime = log_datetime
                                    attendance.out_direction = 'Manual' if is_manual else 'Machine'
                                    attendance.out_shortname = None if is_manual else log.shortname
                                    update_needed = True
                                
                                # If log_datetime is the same as first_logtime, do not update last_logtime
                                if log_datetime == attendance.first_logtime:
                                    attendance.last_logtime = None

                                if not update_needed:
                                    return True  # No changes required

                                # Recalculate metrics regardless of newness
                                in_datetime = attendance.first_logtime
                                out_datetime = attendance.last_logtime
                                total_time = out_datetime - in_datetime

                                # Apply lunch deduction
                                # if auto_shift.include_lunch_break_in_half_day|auto_shift.include_lunch_break_in_full_day:
                                #     total_time -= auto_shift.lunch_duration or timedelta()

                                if auto_shift.include_lunch_break_in_half_day and total_time >= auto_shift.lunch_duration:
                                    total_time -= auto_shift.lunch_duration
                                    attendance.total_time = total_time
                                    # print(f"Total Time after half day lunch deduction: {attendance.total_time}")
                                else:
                                    if auto_shift.include_lunch_break_in_full_day and total_time >= auto_shift.lunch_duration:
                                        total_time -= auto_shift.lunch_duration
                                        attendance.total_time = total_time
                                        # print(f"Total Time after full day lunch deduction: {attendance.total_time}")
                                    else:
                                        attendance.total_time = total_time

                                # attendance.total_time = total_time

                                # Late entry/early exit
                                shift_start = timezone.make_aware(
                                            datetime.combine(attendance.logdate, auto_shift.start_time),
                                            log_datetime.tzinfo  
                                        )
                                shift_end = timezone.make_aware(
                                            datetime.combine(attendance.logdate, auto_shift.end_time),
                                            log_datetime.tzinfo  
                                        )
                                
                                attendance.late_entry = (
                                    (in_datetime - shift_start) 
                                    if in_datetime > (shift_start + auto_shift.grace_period_at_start_time) 
                                    else None
                                )
                                attendance.early_exit = (
                                    (shift_end - out_datetime) 
                                    if out_datetime < (shift_end - auto_shift.grace_period_at_end_time) 
                                    else None
                                )

                                # Overtime
                                overtime_before = max(
                                    timedelta(), 
                                    (shift_start - in_datetime)
                                ) if in_datetime < (shift_start - auto_shift.overtime_threshold_before_start) else timedelta()
                                
                                overtime_after = max(
                                    timedelta(), 
                                    (out_datetime - shift_end)
                                ) if out_datetime > (shift_end + auto_shift.overtime_threshold_after_end) else timedelta()

                                first_weekoff = employee.first_weekly_off
                                if isinstance(first_weekoff, str):
                                    try:
                                        first_weekoff = int(first_weekoff)
                                    except ValueError:
                                        raise ValueError
                                    
                                second_weekoff = employee.second_weekly_off
                                if isinstance(second_weekoff, str):
                                    try:
                                        second_weekoff = int(second_weekoff)
                                    except ValueError:
                                        raise ValueError
                                # weekoff_days = [first_weekoff] if first_weekoff is not None else WEEK_OFF_CONFIG.get('DEFAULT_WEEK_OFF', [])

                                weekoff_days = []

                                if first_weekoff is not None:
                                    weekoff_days.append(first_weekoff)

                                if second_weekoff is not None:
                                    weekoff_days.append(second_weekoff)
                                
                                # If no week off days were found, fall back to the default week off configuration
                                if not weekoff_days:
                                    weekoff_days = WEEK_OFF_CONFIG.get('DEFAULT_WEEK_OFF', [])
                                
                                if attendance.logdate.weekday() in weekoff_days:
                                    attendance.overtime = total_time
                                else:                        
                                    attendance.overtime = overtime_before + overtime_after if (overtime_before + overtime_after) > timedelta() else None
            

                                # Dynamic status calculation
                                if attendance.logdate in self.holidays:
                                    holiday = self.holidays[attendance.logdate]
                                    attendance.shift_status = 'PW' if holiday.holiday_type == "PH" else 'FW'
                                elif attendance.logdate.weekday() in weekoff_days:
                                    attendance.shift_status = 'WW'
                                elif total_time < auto_shift.absent_threshold:
                                    attendance.shift_status = 'A'  # Will override previous "A" if logs are added
                                elif total_time < auto_shift.half_day_threshold:
                                    attendance.shift_status = 'HD'
                                elif total_time < auto_shift.full_day_threshold:
                                    attendance.shift_status = 'IH'
                                else:
                                    attendance.shift_status = 'P'

                                attendance.save()
                                return True
                    except Exception as e:
                        # self.logger.error(f"Error processing shift {auto_shift.name} for employee {employee.employee_id} in _handle_inout_log: {str(e)}")
                        return False

            # No night shifts

            with transaction.atomic():
                attendance = Attendance.objects.select_for_update().filter(
                    employeeid=employee, 
                    logdate=shift_date
                ).first()

                if attendance and attendance.first_logtime is None:
                    # If attendance exists but no IN time, set IN time
                    attendance.first_logtime = log_datetime                    
                    attendance.shift = shift.name
                    attendance.in_direction = 'Manual' if is_manual else 'Machine'
                    attendance.out_direction = None
                    attendance.shift_status = 'MP'
                    attendance.save()
                    return True

                if not attendance:
                    # Create new attendance without hardcoded status
                    attendance = Attendance(
                        employeeid=employee,
                        logdate=shift_date,
                        first_logtime=log_datetime,
                        last_logtime=None,
                        shift=shift.name,
                        in_direction='Manual' if is_manual else 'Machine',
                        out_direction=None,
                    )
                    attendance.save()  # Save first to generate ID

                update_needed = False

                # Update first/last logtimes if needed
                if (attendance.first_logtime is None or log_datetime < attendance.first_logtime):
                    attendance.first_logtime = log_datetime
                    update_needed = True
                if (attendance.last_logtime is None or (log_datetime > attendance.last_logtime and log_datetime > attendance.first_logtime)):
                    attendance.last_logtime = log_datetime
                    update_needed = True

                # If log_datetime is the same as first_logtime, do not update last_logtime
                if log_datetime == attendance.first_logtime:
                    attendance.last_logtime = None

                if not update_needed:
                    return True  # No changes required

                if not update_needed:
                    return True  # No changes required

                # Recalculate metrics regardless of newness
                in_datetime = attendance.first_logtime
                out_datetime = attendance.last_logtime
                total_time = out_datetime - in_datetime

                # Apply lunch deduction
                if shift.include_lunch_break_in_half_day|shift.include_lunch_break_in_full_day:
                    total_time -= shift.lunch_duration or timedelta()

                attendance.total_time = total_time

                # Late entry/early exit
                shift_start = datetime.combine(shift_date, shift.start_time)
                shift_start = timezone.make_aware(
                            datetime.combine(shift_date, shift.start_time),
                            log_datetime.tzinfo  
                        )
                shift_end = timezone.make_aware(
                            datetime.combine(shift_date, shift.end_time),
                            log_datetime.tzinfo  
                        )
                
                attendance.late_entry = (
                    (in_datetime - shift_start) 
                    if in_datetime > (shift_start + shift.grace_period_at_start_time) 
                    else None
                )
                attendance.early_exit = (
                    (shift_end - out_datetime) 
                    if out_datetime < (shift_end - shift.grace_period_at_end_time) 
                    else None
                )

                # Overtime
                overtime_before = max(
                    timedelta(), 
                    (shift_start - shift.overtime_threshold_before_start) - in_datetime
                ) if in_datetime < (shift_start - shift.overtime_threshold_before_start) else timedelta()
                
                overtime_after = max(
                    timedelta(), 
                    out_datetime - (shift_end + shift.overtime_threshold_after_end)
                ) if out_datetime > (shift_end + shift.overtime_threshold_after_end) else timedelta()
                
                attendance.overtime = overtime_before + overtime_after or None

                # Dynamic status calculation
                if attendance.logdate in self.holidays:
                    holiday = self.holidays[attendance.logdate]
                    attendance.shift_status = 'PW' if holiday.holiday_type == "PH" else 'FW'
                elif attendance.logdate.weekday() in WEEK_OFF_CONFIG.get('DEFAULT_WEEK_OFF', []):
                    attendance.shift_status = 'WW'
                elif total_time < shift.absent_threshold:
                    attendance.shift_status = 'A'  # Will override previous "A" if logs are added
                elif total_time < shift.half_day_threshold:
                    attendance.shift_status = 'HD'
                elif total_time < shift.full_day_threshold:
                    attendance.shift_status = 'IH'
                else:
                    attendance.shift_status = 'P'

                attendance.save()
                return True

        except Exception as e:
            # self.logger.error(f"Error processing in/out log: {str(e)}")
            return False