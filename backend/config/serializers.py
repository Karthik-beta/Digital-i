from rest_framework import serializers
from datetime import timedelta, datetime, date
from config import models


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = '__all__'

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['name'] = instance.name.title()
    #     return data

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = '__all__'

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Designation
        fields = '__all__'

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Division
        fields = '__all__'

class SubDivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubDivision
        fields = '__all__'

class ShopfloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Shopfloor
        fields = '__all__'

class ShiftSerializer(serializers.ModelSerializer):
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
                raise serializers.ValidationError("Duration must be a valid integer number of minutes")

    # Duration fields
    tolerance_before_start_time = DurationMinutesField(required=False, allow_null=True)
    tolerance_after_start_time = DurationMinutesField(required=False, allow_null=True)
    tolerance_before_end_time = DurationMinutesField(required=False, allow_null=True)
    tolerance_after_end_time = DurationMinutesField(required=False, allow_null=True)
    grace_period_at_start_time = DurationMinutesField(required=False, allow_null=True)
    grace_period_at_end_time = DurationMinutesField(required=False, allow_null=True)
    overtime_threshold_before_start = DurationMinutesField(required=False, allow_null=True)
    overtime_threshold_after_end = DurationMinutesField(required=False, allow_null=True)
    absent_threshold = DurationMinutesField(required=False, allow_null=True)
    half_day_threshold = DurationMinutesField(required=False, allow_null=True)
    full_day_threshold = DurationMinutesField(required=False, allow_null=True)
    
    # Time fields
    start_time = serializers.TimeField(format='%H:%M:%S')
    end_time = serializers.TimeField(format='%H:%M:%S')
    lunch_in = serializers.TimeField(format='%H:%M:%S', required=False, allow_null=True)
    lunch_out = serializers.TimeField(format='%H:%M:%S', required=False, allow_null=True)
    
    class Meta:
        model = models.Shift
        fields = [
            'id', 'shift_id', 'name', 'start_time', 'end_time',
            'tolerance_before_start_time', 'tolerance_after_start_time',
            'tolerance_before_end_time', 'tolerance_after_end_time',
            'grace_period_at_start_time', 'grace_period_at_end_time',
            'overtime_threshold_before_start', 'overtime_threshold_after_end',
            'absent_threshold', 'half_day_threshold', 'full_day_threshold',
            'lunch_in', 'lunch_out', 'lunch_duration',
            'night_shift', 'include_lunch_break_in_half_day',
            'include_lunch_break_in_full_day', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'lunch_duration')

    def validate(self, data):
        """Validate the AutoShift data."""
        validated_data = data.copy()
        
        # Handle lunch times
        lunch_in = validated_data.get('lunch_in')
        lunch_out = validated_data.get('lunch_out')

        # Calculate lunch duration if both times are provided
        if lunch_in and lunch_out and lunch_in != "00:00:00" and lunch_out != "00:00:00":
            lunch_in_dt = datetime.combine(date.today(), lunch_in)
            lunch_out_dt = datetime.combine(date.today(), lunch_out)
            
            if lunch_out_dt < lunch_in_dt:
                lunch_out_dt = datetime.combine(date.today() + timedelta(days=1), lunch_out)
            
            validated_data['lunch_duration'] = lunch_out_dt - lunch_in_dt
        else:
            validated_data['lunch_duration'] = timedelta(0)
            validated_data['lunch_in'] = None
            validated_data['lunch_out'] = None

        # Set night_shift flag based on start and end times
        # if validated_data.get('start_time') and validated_data.get('end_time'):
        #     is_night = validated_data['start_time'] > validated_data['end_time']
        #     validated_data['night_shift'] = is_night

        return validated_data

    def to_representation(self, instance):
        """Convert the AutoShift instance to a dictionary."""
        data = super().to_representation(instance)
        
        # Format time fields
        time_fields = ['start_time', 'end_time']
        for field in time_fields:
            if data.get(field):
                data[field] = data[field][:8]  # Ensure HH:MM:SS format
                
        # Handle lunch times
        data['lunch_in'] = instance.lunch_in.strftime('%H:%M:%S') if instance.lunch_in else "00:00:00"
        data['lunch_out'] = instance.lunch_out.strftime('%H:%M:%S') if instance.lunch_out else "00:00:00"
        
        # Handle lunch duration
        if instance.lunch_duration:
            total_seconds = int(instance.lunch_duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            data['lunch_duration'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            data['lunch_duration'] = "00:00:00"
            
        return data
    
class AttendanceCorrectionConfigSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.AttendanceCorrectionConfig
        fields = '__all__'