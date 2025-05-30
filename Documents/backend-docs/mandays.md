# ManDays Attendance Processing Logic

This document describes the logic for ManDays attendance processing in the Digital-i backend, as implemented in `backend/resource/mandays.py`.

## Overview

The ManDays attendance processor is responsible for:
- Reading raw punch logs for employees
- Grouping logs by employee and date
- Pairing IN/OUT punches into attendance slots (up to 10 per day)
- Handling night shift scenarios (where OUT punch may occur the next day)
- Calculating total work time per slot and per day
- Storing processed attendance records in the `ManDaysAttendance` model
- Tracking the last processed log to ensure incremental processing

## Key Class: `ManDaysAttendanceProcessor`

### Initialization

- Loads the last processed log ID to avoid reprocessing old logs.
- Caches valid employee IDs and details for efficient lookups.

### Main Methods

- **`process_logs()`**: Entry point for processing new logs. Groups logs, processes each employee's daily logs, and updates attendance records.
- **`_get_new_logs()`**: Fetches new, distinct logs (by employee, datetime, direction) since the last processed log.
- **`_group_logs_by_employee_and_date(logs)`**: Groups logs by employee and date for batch processing.
- **`_process_day_logs(emp_id, current_date, logs, prev_day_record=None)`**: Pairs IN/OUT punches into slots, handles night shift logic, and calculates total time for each slot.
- **`_create_attendance_record(emp_id, log_date, processed_logs)`**: Creates or updates the `ManDaysAttendance` record for the employee and date, filling up to 10 slots and total hours worked.
- **`_get_last_record_info(prev_day_record)`**: Utility to fetch the last IN/OUT info from the previous day's attendance record.
- **`_is_valid_employee(emp_id)`**: Checks if the employee ID is valid and active.

### Night Shift Handling

- If the first punch of the day is an OUT punch and the previous day's record has an unmatched IN, the OUT is paired with the previous day's IN, and total time is calculated across midnight.

### Data Integrity

- All attendance updates are performed within Django transactions for consistency.
- The last processed log ID is updated after successful processing to ensure logs are not reprocessed.

### Error Handling

- Invalid or missing employee IDs are skipped with warnings.
- All exceptions are logged for debugging.

## Extending the Logic

- To support more than 10 IN/OUT slots per day, adjust the slot logic in `_process_day_logs` and `_create_attendance_record`.
- Additional business rules (e.g., overtime, late entry) can be added in the processing methods.

---

For further details, see the code in `backend/resource/mandays.py`.