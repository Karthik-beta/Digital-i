# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.interval import IntervalTrigger
from django.core.management import call_command
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
                    'misfire_grace_time': 60 * 2,  # 5 minutes grace time
                    'coalesce': True,  # Combine multiple missed runs
                    'max_instances': 1
                }
            )
            _scheduler.add_jobstore(DjangoJobStore(), "default")
            
            # Add jobs with better configuration
            _scheduler.add_job(
                run_my_command,
                trigger=IntervalTrigger(
                    minutes=1,
                    timezone=settings.TIME_ZONE
                ),
                id="my_job",
                replace_existing=True
            )
            
            logger.info("Created new scheduler instance")
        return _scheduler
    except Exception as e:
        logger.error(f"Failed to create/get scheduler: {str(e)}")
        return None

def run_my_command():
    """Execute management commands with better error handling"""
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
        
        for command in commands:
            try:
                call_command(command)
                logger.info(f"Successfully executed command: {command}")
            except Exception as e:
                logger.error(f"Error executing command {command}: {str(e)}")
    finally:
        # Always clean up the lock file, even if an exception occurs
        try:
            os.unlink(lock_file)
        except Exception as e:
            logger.error(f"Failed to remove lock file: {str(e)}")

def start_scheduler():
    """Start the scheduler using the global instance"""
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
            print("Scheduler started.")
            return True
        else:
            logger.info("Scheduler is already running")
            return True
            
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
    Returns True if successful or no action needed, False if shutdown failed.
    """
    global _scheduler
    
    if _scheduler is None:
        logger.info("No scheduler instance to shut down")
        return True
        
    try:
        # Check if scheduler exists and attempt to clean up jobs first
        if _scheduler:
            logger.info("Attempting to clean up jobs before shutdown")
            try:
                _scheduler.remove_all_jobs()
                logger.info("All scheduler jobs removed successfully")
            except Exception as job_error:
                logger.warning(f"Could not remove all jobs: {str(job_error)}")
            
            # Check running state and attempt shutdown
            try:
                running = getattr(_scheduler, 'running', False)
                if running:
                    logger.info("Shutting down running scheduler")
                    _scheduler.shutdown(wait=True)
                    logger.info("Scheduler shutdown completed")
                else:
                    logger.info("Scheduler was not in running state")
            except Exception as shutdown_error:
                logger.error(f"Error during scheduler shutdown: {str(shutdown_error)}")
                return False
                
            # Reset the scheduler instance
            _scheduler = None
            logger.info("Scheduler reference cleared")
            return True
        return True
        
    except Exception as e:
        logger.error(f"Critical error in scheduler shutdown: {str(e)}", exc_info=True)
        # Attempt force cleanup even after error
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