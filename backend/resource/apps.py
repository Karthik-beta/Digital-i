from django.apps import AppConfig
from django.core.management import call_command
import sys
import os
import threading
import time
from dotenv import load_dotenv

# Load the correct environment file
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

class ResourceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resource'

    def ready(self):
        # Prevent the scheduler from starting during migrations
        if 'runserver' in sys.argv or 'uwsgi' in sys.argv:
            # Start scheduler in a separate thread to avoid blocking app startup
            def start_scheduler_delayed():
                pid = os.getpid()
                print(f"Process {pid}: Starting delayed scheduler initialization...")
                
                time.sleep(15)  # Wait 15 seconds for Django to fully initialize
                
                try:
                    from . import scheduler
                    
                    # Delayed scheduler start after migrations are checked/applied
                    if ENVIRONMENT != 'local':
                        print(f"Process {pid}: Running migrations and setup commands...")
                        call_command('migrate', interactive=False)
                        print("Migrations applied successfully.")

                        try:
                            call_command('reset_sequences')
                            print("Sequences reset successfully.")
                        except Exception as e:
                            print(f"Failed to reset sequences: {e}")

                        try:
                            call_command('absentees', days=400)
                            print("Absentees command executed successfully.")
                        except Exception as e:
                            print(f"Failed to execute absentees command: {e}")

                        print("Waiting for post_migrate tasks to complete...")
                        time.sleep(2)  # Brief pause after commands
                        
                    # Attempt to start the scheduler with retries
                    max_retries = 3
                    for attempt in range(max_retries):
                        print(f"Process {pid}: Scheduler start attempt {attempt + 1}/{max_retries}")
                        
                        try:
                            success = scheduler.start_scheduler()
                            if success:
                                print(f"Process {pid}: Scheduler started successfully on attempt {attempt + 1}.")
                                
                                # Verify scheduler is actually working
                                time.sleep(3)  # Wait a bit for jobs to be scheduled
                                
                                # Double-check that jobs exist
                                sched_instance = scheduler.get_scheduler()
                                if sched_instance and sched_instance.running:
                                    main_job = sched_instance.get_job("my_job")
                                    monitor_job = sched_instance.get_job("job_monitor")
                                    
                                    if main_job and monitor_job:
                                        print(f"Process {pid}: Scheduler verification successful - both jobs confirmed.")
                                        return  # Success - exit the function
                                    else:
                                        print(f"Process {pid}: Warning - Scheduler started but jobs missing. Main: {main_job is not None}, Monitor: {monitor_job is not None}")
                                        if attempt < max_retries - 1:
                                            continue  # Try again
                                else:
                                    print(f"Process {pid}: Warning - Scheduler not running after start_scheduler returned success.")
                                    if attempt < max_retries - 1:
                                        continue  # Try again
                                        
                            else:
                                print(f"Process {pid}: start_scheduler() returned False on attempt {attempt + 1}")
                                
                        except Exception as e:
                            print(f"Process {pid}: Exception during scheduler start attempt {attempt + 1}: {e}")
                        
                        # If we're here, the attempt failed
                        if attempt < max_retries - 1:
                            print(f"Process {pid}: Waiting 5 seconds before retry...")
                            time.sleep(5)
                    
                    # All attempts failed - try emergency measures
                    print(f"Process {pid}: All scheduler start attempts failed. Trying emergency measures...")
                    try:
                        # Try to get scheduler and force job creation
                        sched_instance = scheduler.get_scheduler()
                        if sched_instance:
                            if not sched_instance.running:
                                print(f"Process {pid}: Emergency: Starting scheduler that wasn't running...")
                                from django_apscheduler.jobstores import register_events
                                register_events(sched_instance)
                                sched_instance.start()
                            
                            # Force add jobs
                            print(f"Process {pid}: Emergency: Force adding jobs...")
                            success = scheduler.emergency_job_recreate() if hasattr(scheduler, 'emergency_job_recreate') else False
                            
                            if success:
                                print(f"Process {pid}: Emergency job recreation successful.")
                            else:
                                print(f"Process {pid}: Emergency job recreation failed.")
                        else:
                            print(f"Process {pid}: Emergency: Could not get scheduler instance.")
                            
                    except Exception as e:
                        print(f"Process {pid}: Emergency measures failed: {e}")
                        
                    print(f"Process {pid}: Scheduler initialization completed with issues. Check logs for job status.")
                        
                except Exception as e:
                    print(f"Process {pid}: Critical error in scheduler initialization: {e}")

            # Start the delayed scheduler in a non-daemon thread for better cleanup
            scheduler_thread = threading.Thread(target=start_scheduler_delayed, daemon=False)
            scheduler_thread.start()