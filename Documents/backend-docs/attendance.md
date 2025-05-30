# Attendance Processing Logic

This document describes the core logic and workflow for attendance processing in the Digital-i backend, as implemented in `backend/resource/attendance.py`.

## Overview

The attendance processing module is responsible for:
- Reading raw attendance logs (from biometric devices or manual entries)
- Determining shift windows and applying shift rules
- Calculating attendance status, overtime, late entry, early exit, and total work time
- Handling both fixed and auto-shift employees
- Bulk processing and atomic updates for data integrity

## Key Classes and Methods

### `AttendanceProcessor`
Main class for processing attendance logs.

#### Initialization
- Loads all shifts, employees, holidays, and device configurations into memory for efficient access.

#### `process_new_logs(batch_size=5000)`
- Processes unprocessed logs in batches.
- For each log, determines if it is manual or device-based and calls `process_single_log`.
- Uses Django transactions for atomicity and bulk-creates processed log records.

#### `process_single_log(log, is_manual=False)`
- Determines the employee and checks employment period.
- Identifies the device and direction (in/out/both).
- Routes the log to the appropriate handler based on shift type (fixed or auto) and direction.

#### Shift Handling Methods
- `_handle_in_log_autoshift`, `_handle_out_log_autoshift`: Handle IN/OUT logs for auto-shift employees.
- `_handle_in_log_fixedshift`, `_handle_out_log_fixedshift`: Handle IN/OUT logs for fixed-shift employees.
- `_handle_inout_log`: Handles logs that represent both IN and OUT in a single entry.
- `_handle_in_after_out`: Handles cases where an IN log is received after an OUT log for the same day.

#### Shift Window Calculation
- `_calculate_autoshift_window(auto_shift, log_datetime, base_date)`: Calculates the valid time window for a shift, including grace periods and overtime thresholds.

## Attendance Calculation Logic

- **Late Entry**: Calculated if IN time is after the shift start plus grace period.
- **Early Exit**: Calculated if OUT time is before the shift end minus grace period.
- **Overtime**: Calculated based on time before shift start or after shift end, considering overtime thresholds.
- **Lunch Break Deduction**: Applied if the shift configuration requires it and the total time exceeds the lunch duration.
- **Status Calculation**: Attendance status is set based on total time, holidays, and week-off configuration:
  - `P`: Present
  - `HD`: Half Day
  - `IH`: Incomplete Hours
  - `A`: Absent
  - `WW`: Weekly Off
  - `PW`: Public Holiday
  - `FW`: Festival Holiday
  - `MP`: Marked Present (pending final calculation)

## Data Integrity

- All updates are performed within Django transactions to ensure consistency.
- Attendance records are locked for update during processing to prevent race conditions.

## Error Handling

- Errors are logged and do not interrupt batch processing.
- If a log cannot be processed, it is skipped and processing continues.

## Extending the Logic

- To add new attendance rules or shift types, extend the relevant handler methods.
- Device configuration and holiday logic can be customized via the respective models.

---

For further details, see the code in `backend/resource/attendance.py`.