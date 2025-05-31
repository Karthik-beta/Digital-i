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
import time
from django.utils import timezone

logger = logging.getLogger(__name__)

# Initialize the global scheduler variable
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
            
            # # Important: Start the scheduler to load existing jobs from jobstore
            # if not _scheduler.running:
            #     register_events(_scheduler)
            #     _scheduler.start()
            #     logger.info("Scheduler started and existing jobs loaded from jobstore")
                
            #     # Log what jobs were loaded
            #     existing_jobs = _scheduler.get_jobs()
            #     logger.info(f"Loaded {len(existing_jobs)} existing jobs from database: {[job.id for job in existing_jobs]}")
        
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
    logger.info("=== JOB EXECUTION STARTED ===")
    logger.info(f"Process PID: {os.getpid()}")
    logger.info(f"Current time: {timezone.now()}")
    
    # First check if the job still exists before running
    try:
        scheduler = get_scheduler()
        if scheduler and scheduler.running:
            job = scheduler.get_job("my_job")
            if job is None:
                logger.error("Job 'my_job' no longer exists! Attempting emergency recreation...")
                emergency_job_recreate()
                return
            else:
                logger.info(f"Job 'my_job' exists. Next run: {job.next_run_time}")
    except Exception as e:
        logger.error(f"Error checking job existence: {str(e)}", exc_info=True)
    
    commands = ['sync_logs', 'sync_all_logs', 'absentees', 'task', 'mandays', 'correct_a_wo_a_pattern', 'revert_awo_corrections']

    logger.info("Starting command execution sequence...")
    
    try:
        # Execute each command safely
        for i, command in enumerate(commands, 1):
            logger.info(f"Executing command {i}/{len(commands)}: {command}")
            success = safe_call_command(command)
            logger.info(f"Command {command} completed with success={success}")
            
    except Exception as e:
        logger.error(f"Unexpected error in run_my_command: {str(e)}", exc_info=True)
    finally:
        logger.info("=== JOB EXECUTION COMPLETED ===")

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

        # Check if main job exists
        try:
            main_job = scheduler.get_job("my_job")
        except Exception as e:
            logger.error(f"Error checking for main job: {str(e)}")
            main_job = None
            
        if main_job is None:
            logger.warning("Job 'my_job' missing! Creating new job...")
            try:
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
                
                # Verify job was actually created
                verify_job = scheduler.get_job("my_job")
                if verify_job is None:
                    logger.error("Job creation verification failed!")
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to create main job: {str(e)}")
                return False
        else:
            # Check if job has a next run time
            if main_job.next_run_time is None:
                logger.warning("Job 'my_job' exists but has no next run time. Rescheduling...")
                try:
                    main_job.reschedule(trigger=IntervalTrigger(
                        minutes=1,
                        timezone=settings.TIME_ZONE
                    ))
                    logger.info("Job 'my_job' rescheduled successfully.")
                except Exception as e:
                    logger.error(f"Failed to reschedule job: {str(e)}")
                    return False
            else:
                logger.debug(f"Job 'my_job' is running normally. Next run: {main_job.next_run_time}")

        # Ensure monitor job also exists
        try:
            monitor_job = scheduler.get_job("job_monitor")
        except Exception as e:
            logger.error(f"Error checking for monitor job: {str(e)}")
            monitor_job = None
            
        if monitor_job is None:
            logger.warning("Monitor job missing! Creating new monitor job...")
            try:
                scheduler.add_job(
                    ensure_job_running,
                    trigger=IntervalTrigger(
                        minutes=5,
                        timezone=settings.TIME_ZONE
                    ),
                    id="job_monitor",
                    replace_existing=True
                )
                logger.info("Job monitor recreated successfully.")
            except Exception as e:
                logger.error(f"Failed to create monitor job: {str(e)}")
                return False

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

        # Scheduler might already be running from get_scheduler()
        if not scheduler.running:
            register_events(scheduler)
            scheduler.start()
            logger.info("Scheduler started successfully")
        else:
            logger.info("Scheduler was already running")

        # Check existing jobs first
        existing_jobs = scheduler.get_jobs()
        logger.info(f"Current jobs in scheduler: {[job.id for job in existing_jobs]}")
        
        main_job = scheduler.get_job("my_job")
        monitor_job = scheduler.get_job("job_monitor")
        
        # Only add jobs if they don't exist
        if main_job is None:
            scheduler.add_job(
                run_my_command,
                trigger=IntervalTrigger(
                    minutes=1,
                    timezone=settings.TIME_ZONE
                ),
                id="my_job",
                replace_existing=True
            )
            logger.info("Job 'my_job' added to the scheduler.")
        else:
            logger.info("Job 'my_job' already exists in scheduler.")

        if monitor_job is None:
            scheduler.add_job(
                ensure_job_running,
                trigger=IntervalTrigger(
                    minutes=5,
                    timezone=settings.TIME_ZONE
                ),
                id="job_monitor",
                replace_existing=True
            )
            logger.info("Job monitoring task added (every 5 minutes).")
        else:
            logger.info("Job 'job_monitor' already exists in scheduler.")

        # Final verification
        main_job = scheduler.get_job("my_job")
        monitor_job = scheduler.get_job("job_monitor")
        
        if main_job and monitor_job:
            logger.info("Both jobs verified in scheduler.")
            return True
        else:
            logger.error(f"Job verification failed. Main job: {main_job is not None}, Monitor job: {monitor_job is not None}")
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
            
            # Don't pause jobs - let them complete naturally
            # Just shutdown with wait to allow current executions to finish
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

def emergency_job_recreate():
    """Emergency function to recreate missing jobs - call this when jobs disappear"""
    try:
        logger.info("Emergency job recreation initiated...")
        scheduler = get_scheduler()
        
        if not scheduler:
            logger.error("No scheduler available for emergency recreation")
            return False
            
        if not scheduler.running:
            logger.warning("Scheduler not running during emergency recreation")
            try:
                register_events(scheduler)
                scheduler.start()
                logger.info("Scheduler started during emergency recreation")
            except Exception as e:
                logger.error(f"Failed to start scheduler during emergency recreation: {str(e)}")
                return False

        # Force recreate main job
        try:
            scheduler.add_job(
                run_my_command,
                trigger=IntervalTrigger(
                    minutes=1,
                    timezone=settings.TIME_ZONE
                ),
                id="my_job",
                replace_existing=True
            )
            logger.info("Emergency: Job 'my_job' recreated")
        except Exception as e:
            logger.error(f"Emergency: Failed to recreate main job: {str(e)}")
            return False

        # Force recreate monitor job
        try:
            scheduler.add_job(
                ensure_job_running,
                trigger=IntervalTrigger(
                    minutes=5,
                    timezone=settings.TIME_ZONE
                ),
                id="job_monitor",
                replace_existing=True
            )
            logger.info("Emergency: Job 'job_monitor' recreated")
        except Exception as e:
            logger.error(f"Emergency: Failed to recreate monitor job: {str(e)}")
            return False

        # Verify recreation
        main_job = scheduler.get_job("my_job")
        monitor_job = scheduler.get_job("job_monitor")
        
        if main_job and monitor_job:
            logger.info("Emergency job recreation completed successfully")
            return True
        else:
            logger.error("Emergency job recreation failed verification")
            return False
            
    except Exception as e:
        logger.error(f"Emergency job recreation failed: {str(e)}")
        return False