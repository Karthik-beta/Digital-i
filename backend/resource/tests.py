import pytest
from django.utils import timezone
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
from django.db import transaction
from .models import Logs, Employee, LastLogId, Attendance
from .attendance5 import process_attendance

@pytest.fixture
def setup_test_data():
    # Create test employees
    employee1 = Employee.objects.create(
        employee_id="EMP001",
        name="Test Employee 1"
    )
    employee2 = Employee.objects.create(
        employee_id="EMP002",
        name="Test Employee 2"
    )
    
    # Create LastLogId 
    LastLogId.objects.create(last_log_id=0)
    
    # Create base datetime for testing
    base_date = timezone.now().date()
    
    # Create test logs
    logs = [
        # Normal day with in and out
        Logs.objects.create(
            id=1,
            employeeid=employee1,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=9)),
            direction="In Device"
        ),
        Logs.objects.create(
            id=2,
            employeeid=employee1,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=17)),
            direction="Out Device"
        ),
        
        # Multiple in/out records
        Logs.objects.create(
            id=3,
            employeeid=employee2,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=8)),
            direction="In Device"
        ),
        Logs.objects.create(
            id=4,
            employeeid=employee2,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=12)),
            direction="Out Device"
        ),
        Logs.objects.create(
            id=5,
            employeeid=employee2,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=13)),
            direction="In Device"
        ),
        Logs.objects.create(
            id=6,
            employeeid=employee2,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=18)),
            direction="Out Device"
        ),
    ]
    
    return {
        'employee1': employee1,
        'employee2': employee2,
        'base_date': base_date,
        'logs': logs
    }

@pytest.mark.django_db
class TestProcessAttendance:
    
    def test_normal_attendance_processing(self, setup_test_data):
        """Test processing of normal attendance with single in and out"""
        # Process attendance
        result = process_attendance()
        
        # Check employee1's attendance
        emp1_attendance = next(
            record for record in result 
            if record['employee_id'] == setup_test_data['employee1']
        )
        
        assert emp1_attendance['log_date'] == setup_test_data['base_date']
        assert emp1_attendance['log_in'].hour == 9
        assert emp1_attendance['log_out'].hour == 17
    
    def test_multiple_logs_same_day(self, setup_test_data):
        """Test processing when employee has multiple in/out logs in same day"""
        result = process_attendance()
        
        # Check employee2's attendance
        emp2_attendance = next(
            record for record in result 
            if record['employee_id'] == setup_test_data['employee2']
        )
        
        # Should take first in and last out
        assert emp2_attendance['log_date'] == setup_test_data['base_date']
        assert emp2_attendance['log_in'].hour == 8
        assert emp2_attendance['log_out'].hour == 18
    
    def test_missing_out_punch(self, setup_test_data):
        """Test processing when employee has only in punch"""
        # Create log with only in punch
        employee = setup_test_data['employee1']
        base_date = setup_test_data['base_date'] + timedelta(days=1)
        
        Logs.objects.create(
            id=7,
            employeeid=employee,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=9)),
            direction="In Device"
        )
        
        result = process_attendance()
        
        # Find the relevant attendance record
        attendance = next(
            record for record in result 
            if record['employee_id'] == employee and record['log_date'] == base_date
        )
        
        assert attendance['log_in'] is not None
        assert attendance['log_out'] is None
    
    def test_missing_in_punch(self, setup_test_data):
        """Test processing when employee has only out punch"""
        # Create log with only out punch
        employee = setup_test_data['employee1']
        base_date = setup_test_data['base_date'] + timedelta(days=1)
        
        Logs.objects.create(
            id=8,
            employeeid=employee,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=17)),
            direction="Out Device"
        )
        
        result = process_attendance()
        
        # Find the relevant attendance record
        attendance = next(
            record for record in result 
            if record['employee_id'] == employee and record['log_date'] == base_date
        )
        
        assert attendance['log_in'] is None
        assert attendance['log_out'] is not None
    
    def test_no_new_logs(self, setup_test_data):
        """Test when there are no new logs after last_log_id"""
        # Update LastLogId to be higher than all existing logs
        LastLogId.objects.all().update(last_log_id=100)
        
        result = process_attendance()
        assert result == []
    
    @patch('django.db.transaction.atomic')
    def test_transaction_handling(self, mock_atomic, setup_test_data):
        """Test that the function uses database transactions"""
        process_attendance()
        mock_atomic.assert_called_once()
    
    def test_log_ordering(self, setup_test_data):
        """Test that logs are processed in chronological order"""
        # Create out-of-order logs
        employee = setup_test_data['employee1']
        base_date = setup_test_data['base_date'] + timedelta(days=1)
        
        # Create logs in reverse order
        Logs.objects.create(
            id=10,
            employeeid=employee,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=17)),
            direction="Out Device"
        )
        Logs.objects.create(
            id=9,
            employeeid=employee,
            log_datetime=datetime.combine(base_date, datetime.min.time().replace(hour=9)),
            direction="In Device"
        )
        
        result = process_attendance()
        
        # Find the relevant attendance record
        attendance = next(
            record for record in result 
            if record['employee_id'] == employee and record['log_date'] == base_date
        )
        
        # Verify chronological processing
        assert attendance['log_in'].hour == 9
        assert attendance['log_out'].hour == 17