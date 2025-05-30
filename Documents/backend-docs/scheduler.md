# Scheduler Logic Documentation

This document describes the scheduler logic for the Digital-i backend, as implemented in `backend/resource/scheduler.py` and initialized via `backend/resource/apps.py`.

## Overview

The scheduler is responsible for running periodic background tasks such as attendance log synchronization, absentee calculation, and other maintenance commands. It uses APScheduler with Django integration to ensure jobs are persistent and robust.

## Key Components

### Initialization

- The scheduler is started in a separate thread when the Django app boots (see `apps.py`).
- It waits for migrations and setup commands to complete before starting.
- Multiple retries and verification steps ensure the scheduler and its jobs are reliably started.

### Scheduler Implementation (`scheduler.py`)

- Uses `BackgroundScheduler` from APScheduler with `DjangoJobStore` for persistence.
- Jobs are protected against overlapping runs and missed executions (via `coalesce` and `misfire_grace_time`).
- Main jobs:
  - **my_job**: Runs core management commands every minute.
  - **job_monitor**: Ensures the main job is always present and running (runs every 5 minutes).

### Main Functions

- `get_scheduler()`: Returns or creates the global scheduler instance.
- `start_scheduler()`: Starts the scheduler and ensures jobs are scheduled.
- `run_my_command()`: Executes a sequence of Django management commands with error handling.
- `ensure_job_running()`: Failsafe to guarantee the main job and monitor job are always running.
- `emergency_job_recreate()`: Recreates jobs if they are missing or the scheduler is restarted.
- `pause_scheduler()` / `resume_scheduler()`: Pause and resume all scheduled jobs.
- `shutdown_scheduler()`: Safely shuts down the scheduler, preserving jobs for restart.

### Job Management

- Jobs are identified by unique IDs (`my_job`, `job_monitor`).
- The scheduler verifies job existence and recreates them if missing.
- All job operations are logged for traceability and debugging.

### Error Handling & Reliability

- Multiple retries and emergency measures are implemented to handle scheduler or job failures.
- All exceptions are logged, and the system attempts to recover automatically.
- The scheduler is only started after migrations and setup commands are completed to avoid race conditions.

## Extending the Scheduler

- To add new periodic tasks, define a new function and add it as a job in `start_scheduler()`.
- Adjust intervals and job logic as needed for your use case.

---

For further details, see the code in `backend/resource/scheduler.py` and `backend/resource/apps.py`.