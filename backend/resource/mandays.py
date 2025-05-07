from datetime import datetime, timedelta, date, time
from django.db.models import Q
from django.db import transaction
from typing import List, Dict, Tuple
import logging
from tqdm import tqdm

from resource.models import Logs, Employee, ManDaysAttendance, LastLogIdMandays

logger = logging.getLogger(__name__)

class ManDaysAttendanceProcessor:
    def __init__(self):
        self.last_processed_id = self._get_last_processed_id()
        self.valid_employee_ids = self._get_valid_employee_ids()
        self.employee_details = self._get_employee_details()
        
    def _get_last_processed_id(self) -> int:
        last_log = LastLogIdMandays.objects.first()
        return last_log.last_log_id if last_log else 0
    
    def _get_valid_employee_ids(self) -> set:
        return set(Employee.objects.values_list('employee_id', flat=True))

    def _get_employee_details(self) -> Dict:
        employee_data = {str(emp['employee_id']): emp for emp in Employee.objects.values('id', 'employee_id')}
        return employee_data

    def _get_new_logs(self) -> List:
        """Get new logs with distinct employee punches."""
        distinct_fields = ['employeeid', 'log_datetime', 'direction']
        order_fields = distinct_fields + ['id']
        
        return (Logs.objects
                .filter(id__gt=self.last_processed_id)
                .order_by(*order_fields)
                .distinct(*distinct_fields)
                .values('id', 'employeeid', 'log_datetime', 'direction'))

    def _get_last_record_info(self, prev_day_record: ManDaysAttendance) -> Tuple[int, str, time, bool]:
        """Get info about the last record from previous day."""
        last_index = 0
        last_direction = None
        last_time = None
        has_out = False

        for i in range(1, 11):
            in_time = getattr(prev_day_record, f'duty_in_{i}', None)
            out_time = getattr(prev_day_record, f'duty_out_{i}', None)
            
            if in_time is not None:
                last_index = i
                last_direction = 'In Device'
                last_time = in_time
                
            if out_time is not None:
                last_index = i
                last_direction = 'Out Device'
                last_time = out_time
                has_out = True
                
            if in_time is None and out_time is None:
                break

        return last_index, last_direction, last_time, has_out

    def _process_day_logs(self, emp_id: str, current_date: date, logs: List, prev_day_record: ManDaysAttendance = None) -> List[Dict]:
        """Process logs for a single day, handling night shift scenarios."""
        processed_logs = []
        slot_index = 1

        # Sort logs chronologically
        sorted_logs = sorted(logs, key=lambda x: x['log_datetime'])
        
        # Only proceed with night shift handling if there are logs and first punch is Out Device
        if sorted_logs and sorted_logs[0]['direction'] == 'Out Device' and prev_day_record:
            last_idx = 0
            last_in_time = None
            
            # Find the last duty_in without duty_out from previous day
            for i in range(10, 0, -1):
                in_time = getattr(prev_day_record, f'duty_in_{i}', None)
                out_time = getattr(prev_day_record, f'duty_out_{i}', None)
                
                if in_time is not None:
                    if out_time is None:
                        last_idx = i
                        last_in_time = in_time
                    break
            
            # If we found a duty_in without duty_out, copy the first out punch
            if last_idx > 0 and last_in_time:
                first_out_time = sorted_logs[0]['log_datetime'].time()
                setattr(prev_day_record, f'duty_out_{last_idx}', first_out_time)
                
                # Calculate total time for previous day
                in_dt = datetime.combine(current_date - timedelta(days=1), last_in_time)
                out_dt = datetime.combine(current_date, first_out_time)
                if out_dt > in_dt:
                    total_time = out_dt - in_dt
                    setattr(prev_day_record, f'total_time_{last_idx}', total_time)
                
                # Recalculate total_hours_worked for previous day
                total_hours = timedelta()
                for i in range(1, 11):
                    slot_total = getattr(prev_day_record, f'total_time_{i}', None)
                    if slot_total:
                        total_hours += slot_total
                
                prev_day_record.total_hours_worked = total_hours
                
                prev_day_record.save()
        
        # Process current day's logs
        current_in_time = None
        
        for log in sorted_logs:
            if slot_index > 10:
                break

            log_time = log['log_datetime'].time()
            
            if log['direction'] == 'In Device':
                current_in_time = log_time
                processed_logs.append({
                    'slot': slot_index,
                    'duty_in': log_time,
                    'duty_out': None,
                    'total_time': None
                })
                slot_index += 1
            else:  # Out Device
                # Try to pair with previous in time
                if current_in_time and processed_logs and processed_logs[-1]['duty_out'] is None:
                    processed_logs[-1]['duty_out'] = log_time
                    
                    # Calculate total time
                    in_dt = datetime.combine(current_date, current_in_time)
                    out_dt = datetime.combine(current_date, log_time)
                    if out_dt < in_dt:  # Handle midnight crossing
                        out_dt += timedelta(days=1)
                    if out_dt > in_dt:
                        processed_logs[-1]['total_time'] = out_dt - in_dt
                    
                    current_in_time = None
                else:
                    # Create new record if can't pair
                    processed_logs.append({
                        'slot': slot_index,
                        'duty_in': None,
                        'duty_out': log_time,
                        'total_time': None
                    })
                    slot_index += 1

        return processed_logs

    def _group_logs_by_employee_and_date(self, logs: List) -> Dict:
        grouped_logs = {}
        logger.info(f"Grouping logs by employee and date {grouped_logs}")
        for log in logs:
            emp_id = log['employeeid']
            
            if not self._is_valid_employee(emp_id):
                logger.warning(f"Skipping log for invalid employee ID: {emp_id}")
                continue
                
            log_date = log['log_datetime'].date()
            
            if emp_id not in grouped_logs:
                grouped_logs[emp_id] = {}
            if log_date not in grouped_logs[emp_id]:
                grouped_logs[emp_id][log_date] = []
                
            grouped_logs[emp_id][log_date].append(log)
    
        return grouped_logs

    def _create_attendance_record(self, emp_id: str, log_date: date, processed_logs: List[Dict]) -> None:
        try:
            if not self._is_valid_employee(emp_id):
                # logger.warning(f"Skipping attendance record for invalid employee ID: {emp_id}")
                return
                
            empid_id = self.employee_details[emp_id]['id']
            attendance_data = {
                'employeeid_id': empid_id,
                'logdate': log_date,
                'shift': '',
                'shift_status': ''
            }
            
            total_hours = timedelta()
            
            for log in processed_logs:
                slot = log['slot']
                if slot > 10:
                    break
                    
                if log['duty_in']:
                    attendance_data[f'duty_in_{slot}'] = log['duty_in']
                if log['duty_out']:
                    attendance_data[f'duty_out_{slot}'] = log['duty_out']
                if log['total_time']:
                    attendance_data[f'total_time_{slot}'] = log['total_time']
                    total_hours += log['total_time']
            
            attendance_data['total_hours_worked'] = total_hours
            
            ManDaysAttendance.objects.update_or_create(
                employeeid_id=empid_id,
                logdate=log_date,
                defaults=attendance_data
            )
            
        except Exception as e:
            logger.error(f"Error creating attendance record for employee {empid_id}: {str(e)}")

    def _is_valid_employee(self, emp_id: str) -> bool:
        try:
            is_valid = emp_id in self.valid_employee_ids
            # return emp_id in self.valid_employee_ids
            return is_valid
        except (ValueError, TypeError):
            logger.warning(f"Invalid employee ID format: {emp_id}")
            return False

    @transaction.atomic
    def process_logs(self) -> None:
        try:
            new_logs = self._get_new_logs()
            if not new_logs:
                print("No new logs to process")
                return
                
            grouped_logs = self._group_logs_by_employee_and_date(new_logs)
            total_iterations = sum(len(date_logs) for date_logs in grouped_logs.values())
            
            with tqdm(total=total_iterations, desc="Processing attendance logs") as pbar:
                for emp_id, date_logs in grouped_logs.items():
                    sorted_dates = sorted(date_logs.keys())
                    
                    for i, log_date in enumerate(sorted_dates):
                        # Get previous day's record if exists
                        prev_day_record = None
                        if i > 0:
                            empid_id = self.employee_details[emp_id]['id']
                            prev_day = sorted_dates[i - 1]
                            prev_day_record = ManDaysAttendance.objects.filter(
                                employeeid_id=empid_id,
                                logdate=prev_day
                            ).first()
                            
                        processed_logs = self._process_day_logs(
                            emp_id, 
                            log_date, 
                            date_logs[log_date],
                            prev_day_record
                        )
                        
                        if processed_logs:                            
                            self._create_attendance_record(emp_id, log_date, processed_logs)
                        pbar.update(1)
            
            if new_logs:
                self._update_last_processed_id(new_logs.last()['id'])
                
        except Exception as e:
            logger.error(f"Error processing logs: {str(e)}")
            raise

    def _update_last_processed_id(self, log_id: int) -> None:
        LastLogIdMandays.objects.update_or_create(
            defaults={'last_log_id': log_id}
        )