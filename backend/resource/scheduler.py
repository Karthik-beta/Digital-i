# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.interval import IntervalTrigger
from django.core.management import call_command
from django.core.management.base import CommandError
import logging
from django.conf import settings
import os
import tempfile

logger = logging.getLogger(__name__)

_scheduler = None
_paused_jobs = {}

def get_scheduler():
    """Get or create the global scheduler instance"""
    global _scheduler
    try:
        if _scheduler is None:
            _scheduler = BackgroundScheduler(
                timezone=settings.TIME_ZONE,
                job_defaults={
                    'misfire_grace_time': 60 * 2,  # 2 minutes grace time
                    'coalesce': True,  # Combine multiple missed runs
                    'max_instances': 1  # Prevent overlapping job instances
                }
            )
            _scheduler.add_jobstore(DjangoJobStore(), "default")
            logger.info("Created new scheduler instance")
        return _scheduler
    except Exception as e:
        logger.error(f"Failed to create/get scheduler: {str(e)}")
        return None

def safe_call_command(command):
    """Safely call a management command with comprehensive error handling"""
    try:
        call_command(command)
        logger.info(f"Successfully executed command: {command}")
        return True
    except SystemExit as e:
        logger.warning(f"Command {command} exited with SystemExit code {e.code}. Continuing with next command.")
        return False
    except CommandError as e:
        logger.warning(f"Command {command} failed with CommandError: {str(e)}. Continuing with next command.")
        return False
    except Exception as e:
        logger.error(f"Command {command} failed with unexpected error: {str(e)}. Continuing with next command.")
        return False

def run_my_command():
    """Execute management commands with better error handling and job protection"""
    commands = ['sync_logs', 'sync_all_logs', 'absentees', 'task', 'mandays', 'correct_a_wo_a_pattern', 'revert_awo_corrections']

    lock_file = os.path.join(tempfile.gettempdir(), "digitali_commands.lock")

    # Try to create the lock file - this is atomic at the OS level
    try:
        lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        logger.info("Skipping command execution - another process is already running")
        return
    
    try:
        # Write the current PID to the lock file for debugging
        os.write(lock_fd, str(os.getpid()).encode())
        os.close(lock_fd)
        
        # Execute each command safely
        for command in commands:
            safe_call_command(command)
            
    except Exception as e:
        logger.error(f"Unexpected error in run_my_command: {str(e)}")
    finally:
        # Always clean up the lock file, even if an exception occurs
        try:
            os.unlink(lock_file)
        except Exception as e:
            logger.error(f"Failed to remove lock file: {str(e)}")

def ensure_job_running():
    """Ensure the main job is always running - this is our failsafe"""
    try:
        scheduler = get_scheduler()
        if not scheduler:
            logger.error("No scheduler available")
            return False
            
        if not scheduler.running:
            logger.warning("Scheduler not running, attempting to start...")
            try:
                register_events(scheduler)
                scheduler.start()
                logger.info("Scheduler started successfully")
            except Exception as e:
                logger.error(f"Failed to start scheduler: {str(e)}")
                return False

        # Check if job exists
        job = scheduler.get_job("my_job")
        if job is None:
            logger.warning("Job 'my_job' missing! Creating new job...")
            scheduler.add_job(
                run_my_command,
                trigger=IntervalTrigger(
                    minutes=1,
                    timezone=settings.TIME_ZONE
                ),
                id="my_job",
                replace_existing=True
            )
            logger.info("Job 'my_job' created successfully.")
            return True
        else:
            # Check if job has a next run time
            if job.next_run_time is None:
                logger.warning("Job 'my_job' exists but has no next run time. Rescheduling...")
                job.reschedule(trigger=IntervalTrigger(
                    minutes=1,
                    timezone=settings.TIME_ZONE
                ))
                logger.info("Job 'my_job' rescheduled successfully.")
            else:
                logger.debug(f"Job 'my_job' is running normally. Next run: {job.next_run_time}")
            return True
            
    except Exception as e:
        logger.error(f"Error ensuring job is running: {str(e)}")
        return False

def start_scheduler():
    """Start the scheduler and ensure jobs are properly configured"""
    global _scheduler

    try:
        # Use the global scheduler instance
        scheduler = get_scheduler()
        if scheduler is None:
            logger.error("Failed to get scheduler instance")
            return False

        # Only start if not already running
        if not scheduler.running:
            register_events(scheduler)
            scheduler.start()
            logger.info("Scheduler started successfully")

        # Always ensure the main job exists
        scheduler.add_job(
            run_my_command,
            trigger=IntervalTrigger(
                minutes=1,
                timezone=settings.TIME_ZONE
            ),
            id="my_job",
            replace_existing=True
        )
        logger.info("Job 'my_job' added/updated in the scheduler.")

        # Add a more frequent job verification task - every 2 minutes
        scheduler.add_job(
            ensure_job_running,
            trigger=IntervalTrigger(
                minutes=2, 
                timezone=settings.TIME_ZONE
            ),
            id="job_monitor",
            replace_existing=True
        )
        logger.info("Job monitoring task added (every 2 minutes).")

        # Verify job was added successfully
        if scheduler.get_job("my_job"):
            logger.info("Job 'my_job' verified in scheduler.")
            return True
        else:
            logger.error("Failed to verify job 'my_job' in scheduler.")
            return False

    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        return False

def pause_scheduler():
    """Pause all jobs without stopping the scheduler"""
    global _paused_jobs
    scheduler = get_scheduler()
    if scheduler:
        try:
            _paused_jobs = {}
            for job in scheduler.get_jobs():
                _paused_jobs[job.id] = job.next_run_time
                job.pause()
            logger.info("All scheduler jobs paused")
            return True
        except Exception as e:
            logger.error(f"Failed to pause scheduler: {str(e)}")
    return False

def resume_scheduler():
    """Resume all paused jobs"""
    global _paused_jobs
    scheduler = get_scheduler()
    if scheduler:
        try:
            for job in scheduler.get_jobs():
                if job.id in _paused_jobs:
                    job.resume()
            _paused_jobs = {}
            logger.info("All scheduler jobs resumed")
            return True
        except Exception as e:
            logger.error(f"Failed to resume scheduler: {str(e)}")
    return False

def shutdown_scheduler():
    """
    Safely shutdown the scheduler with comprehensive error handling.
    Jobs are preserved in the jobstore for restart.
    Returns True if successful or no action needed, False if shutdown failed.
    """
    global _scheduler

    if _scheduler is None:
        logger.info("No scheduler instance to shut down")
        return True

    try:
        # Check running state and attempt shutdown
        running = getattr(_scheduler, 'running', False)
        if running:
            logger.info("Shutting down running scheduler...")
            
            # First, pause all jobs to prevent new executions
            try:
                for job in _scheduler.get_jobs():
                    job.pause()
                logger.info("All jobs paused before shutdown")
            except Exception as e:
                logger.warning(f"Failed to pause jobs before shutdown: {str(e)}")
            
            # Shutdown with a reasonable wait time to allow current jobs to complete
            _scheduler.shutdown(wait=True)
            logger.info("Scheduler shutdown completed")
        else:
            logger.info("Scheduler was not in running state")

        # Reset scheduler to None after successful shutdown
        _scheduler = None
        logger.info("Scheduler reference cleared")
        return True

    except Exception as e:
        logger.error(f"Error during scheduler shutdown: {str(e)}", exc_info=True)
        # Force reset scheduler reference even if shutdown failed
        _scheduler = None
        return False

def cleanup_scheduler_jobs():
    """
    Remove all jobs from the scheduler before restarting.
    """
    try:
        scheduler = get_scheduler()
        if scheduler:
            scheduler.remove_all_jobs()
            logger.info("All jobs cleared from the scheduler.")
    except Exception as e:
        logger.error(f"Error clearing scheduler jobs: {str(e)}")

def verify_and_restore_job():
    """This function is now replaced by ensure_job_running for better reliability"""
    return ensure_job_running()

def ensure_job_exists():
    """
    Utility function to ensure the main job exists in the scheduler.
    Call this after starting the scheduler to guarantee job presence.
    """
    try:
        scheduler = get_scheduler()
        if scheduler and scheduler.running:
            # Check if job exists
            try:
                job = scheduler.get_job("my_job")
                if job is None:
                    # Add the job
                    scheduler.add_job(
                        run_my_command,
                        trigger=IntervalTrigger(
                            minutes=1,
                            timezone=settings.TIME_ZONE
                        ),
                        id="my_job",
                        replace_existing=True
                    )
                    logger.info("Job 'my_job' ensured in scheduler.")
                    return True
                else:
                    logger.info("Job 'my_job' already exists.")
                    return True
            except JobLookupError:
                # Job doesn't exist, add it
                scheduler.add_job(
                    run_my_command,
                    trigger=IntervalTrigger(
                        minutes=1,
                        timezone=settings.TIME_ZONE
                    ),
                    id="my_job",
                    replace_existing=True
                )
                logger.info("Job 'my_job' ensured in scheduler.")
                return True
        return False
    except Exception as e:
        logger.error(f"Error ensuring job exists: {str(e)}")
        return False