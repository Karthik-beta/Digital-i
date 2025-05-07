import schedule
import time
import subprocess

def run_task():
    try:
        # Run the first Docker command in the background
        subprocess.Popen(["docker", "exec", "skf_mys-django-1", "python", "manage.py", "task"])
    except Exception as e:
        print(f"Error running 'task' command: {e}")

    try:
        # Run the second Docker command in the background
        subprocess.Popen(["docker", "exec", "skf_mys-django-1", "python", "manage.py", "absentees"])
    except Exception as e:
        print(f"Error running 'absentees' command: {e}")

# Schedule the tasks to run every minute
schedule.every(1).minutes.do(run_task)

# Run the schedule in the background
while True:
    schedule.run_pending()
    time.sleep(1)
