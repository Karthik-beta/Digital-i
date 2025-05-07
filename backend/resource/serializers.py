from rest_framework import serializers
from resource.models import (Employee, Attendance, Logs, AllLogs, LastLogId, ManDaysAttendance, ManDaysMissedPunchAttendance, OvertimeRoundoffRules, HolidayList, ExternalDatabaseCredential, BiometricDeviceConfiguration)
from datetime import timedelta
from django.utils import timezone

# from config import models as config
# from config.models import config

class EmployeeSerializer(serializers.ModelSerializer):
    company_name = serializers.PrimaryKeyRelatedField(read_only=True, source='company.name')
    location_name = serializers.PrimaryKeyRelatedField(read_only=True, source='location.name')
    department_name = serializers.PrimaryKeyRelatedField(read_only=True, source='department.name')
    designation_name = serializers.PrimaryKeyRelatedField(read_only=True, source='designation.name')
    division_name = serializers.PrimaryKeyRelatedField(read_only=True, source='division.name')
    subdivision_name = serializers.PrimaryKeyRelatedField(read_only=True, source='subdivision.name')
    shopfloor_name = serializers.PrimaryKeyRelatedField(read_only=True, source='shopfloor.name')
    fixed_shift_name = serializers.PrimaryKeyRelatedField(read_only=True, source='shift.name')
    
    class Meta:
        model = Employee
        fields = '__all__'

    def to_internal_value(self, data):
        """
        Override to handle cases where shift is 0 or a string instead of pk.
        Ensure mutable data before modifying.
        """
        # Make sure the data dictionary is mutable
        data = data.copy()

        if 'shift' in data:
            shift_value = data.get('shift')
            # If shift is "0" or any invalid value, convert it to None
            if shift_value in ['0', 'NaN', 'null', None, '']:
                data['shift'] = None
            else:
                try:
                    # Convert string to integer (to ensure pk value is passed)
                    data['shift'] = int(shift_value)
                except (ValueError, TypeError):
                    raise serializers.ValidationError({'shift': 'Incorrect type. Expected pk value, received invalid value.'})

        return super().to_internal_value(data)

class EmployeeDropdownSerializer(serializers.ModelSerializer):
    combined_field = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['employee_id', 'combined_field']
    
    def get_combined_field(self, obj):
        return f"{obj.employee_name}  [ {obj.employee_id} ]" 


class AttendanceSerializer(serializers.ModelSerializer):
    employee_id_id = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.employee_id')
    profile_pic = serializers.ImageField(read_only=True, source='employeeid.profile_pic') 
    employee_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.employee_name')
    device_enroll_id = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.device_enroll_id')
    company_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.company.name')
    location_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.location.name')
    job_type = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.job_type')
    department_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.department.name')
    category = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.category')
    designation_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.designation.name')
    shift_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.shift.name')

    # Convert datetime fields to local time
    first_logtime = serializers.SerializerMethodField()
    last_logtime = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = '__all__'

    def get_first_logtime(self, obj):
        if obj.first_logtime:
            return timezone.localtime(obj.first_logtime).strftime('%d/%m/%Y %H:%M:%S')
        return None

    def get_last_logtime(self, obj):
        if obj.last_logtime:
            return timezone.localtime(obj.last_logtime).strftime('%d/%m/%Y %H:%M:%S')
        return None


class LogsSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Logs
        fields = '__all__'

    def get_employee_name(self, obj):
        try:
            employee = Employee.objects.get(employee_id=obj.employeeid)
            return employee.employee_name
        except Employee.DoesNotExist:
            return None
        
class AllLogsSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = AllLogs
        fields = '__all__'

    def get_employee_name(self, obj):
        try:
            employee = Employee.objects.get(employee_id=obj.employeeid)
            return employee.employee_name
        except Employee.DoesNotExist:
            return None

class LastLogIdSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LastLogId
        fields = '__all__'

class ManDaysAttendanceSerializer(serializers.ModelSerializer):
    employee_id_id = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.employee_id')
    profile_pic = serializers.ImageField(read_only=True, source='employeeid.profile_pic') 
    employee_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.employee_name')
    device_enroll_id = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.device_enroll_id')
    company_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.company.name')
    location_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.location.name')
    job_type = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.job_type')
    department_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.department.name')
    designation_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.designation.name')
    category = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.category')
    
    class Meta:
        model = ManDaysAttendance
        fields = '__all__'

class ManDaysMissedPunchAttendanceSerializer(serializers.ModelSerializer):
    employee_id_id = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.employee_id')
    profile_pic = serializers.ImageField(read_only=True, source='employeeid.profile_pic') 
    employee_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.employee_name')
    device_enroll_id = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.device_enroll_id')
    company_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.company.name')
    location_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.location.name')
    job_type = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.job_type')
    department_name = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.department.name')
    category = serializers.PrimaryKeyRelatedField(read_only=True, source='employeeid.category')
    
    class Meta:
        model = ManDaysMissedPunchAttendance
        fields = '__all__'

class ResetMandaysResponseSerializer(serializers.Serializer):
    """Serializer for reset mandays response data"""
    message = serializers.CharField()
    cutoff_date = serializers.DateField()
    deleted_records = serializers.IntegerField()
    last_log_id = serializers.IntegerField(allow_null=True)

class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    error = serializers.CharField()
    message = serializers.CharField()

class OvertimeRoundoffRulesSerializer(serializers.ModelSerializer):
    """Serializer for overtime roundoff rules with custom handling for round_off_interval"""

    class DurationMinutesField(serializers.Field):
        """Custom field to handle duration stored as minutes"""
        def to_representation(self, value):
            """Convert timedelta to minutes for output"""
            if value is None:
                return 0
            return int(value.total_seconds() // 60)

        def to_internal_value(self, value):
            """Convert minutes to timedelta for storage"""
            try:
                value = int(value) if value is not None else 0
                return timedelta(minutes=value)
            except (TypeError, ValueError):
                raise serializers.ValidationError("Round-off interval must be a valid integer number of minutes")

    round_off_interval = DurationMinutesField()

    class Meta:
        model = OvertimeRoundoffRules
        fields = '__all__'

class HolidayListSerializer(serializers.ModelSerializer):
    """Serializer for holiday list"""

    class Meta:
        model = HolidayList
        fields = '__all__'

class ExternalDatabaseCredentialSerializer(serializers.ModelSerializer):
    """
    Serializer for External Database Credential
    """

    class Meta:
        model = ExternalDatabaseCredential
        fields = '__all__'

class BiometricDeviceConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for Biometric Device Details
    """
    company_name = serializers.PrimaryKeyRelatedField(read_only=True, source='company.name')
    location_name = serializers.PrimaryKeyRelatedField(read_only=True, source='location.name')

    class Meta:
        model = BiometricDeviceConfiguration
        fields = '__all__'

class DummySerializer(serializers.Serializer):
    pass