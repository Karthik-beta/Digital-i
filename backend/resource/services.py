from random import randint
from django.db import IntegrityError
from .models import Employee
from django.db.models import Max

def generate_unique_ids():
    # Get the maximum existing employee ID
    max_id = Employee.objects.aggregate(Max('employee_id'))['employee_id__max']

    if max_id:
        # Extract the numeric part of the max ID
        max_id_numeric = int(max_id[1:])
    else:
        # If no IDs exist, start from 10000
        max_id_numeric = 10000

    while True:
        # Increment the last generated ID
        max_id_numeric += 1
        # Construct the new employee ID
        employee_id = 'K' + str(max_id_numeric)
        # Construct the new device enroll ID
        device_enroll_id = 'D' + str(max_id_numeric)

        # Check if the generated IDs already exist in the database
        try:
            Employee.objects.get(employee_id=employee_id)
            Employee.objects.get(device_enroll_id=device_enroll_id)
        except Employee.DoesNotExist:
            # If the IDs do not exist, return them
            return employee_id, device_enroll_id
        except IntegrityError:
            # If there was an IntegrityError, continue generating new IDs
            continue


def check_employee_id(employee_id):
    try:
        employee_id = Employee.objects.get(employee_id=employee_id)
        return True
    except Employee.DoesNotExist:
        return False
    