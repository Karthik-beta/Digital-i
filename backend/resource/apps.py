from django.apps import AppConfig
from django.core.management import call_command
import sys
import os
from dotenv import load_dotenv

# Load the correct environment file
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

class ResourceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resource'


    def ready(self):
        # Prevent the scheduler from starting during migrations
        if 'runserver' in sys.argv or 'uwsgi' in sys.argv:
            from . import scheduler
            # Delayed scheduler start after migrations are checked/applied
            try:
                if ENVIRONMENT != 'local':
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

                    # Ensure post_migrate tasks are complete before starting the scheduler
                    print("Waiting for post_migrate tasks to complete...")
                    
                    scheduler.start()
                    print("Scheduler started successfully.")
            except Exception as e:
                print(f"Scheduler failed to start: {e}")