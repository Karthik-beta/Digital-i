from django.db import models
from datetime import timedelta
import datetime

class Company(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    # def save(self, *args, **kwargs):
    #     self.name = self.name.upper()
    #     super(Company, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'company'

class Location(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    # def save(self, *args, **kwargs):
    #     self.name = self.name.title()
    #     super(Location, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'location'

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    # def save(self, *args, **kwargs):
    #     self.name = self.name.upper()
    #     super(Department, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'department'

class Designation(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    # def save(self, *args, **kwargs):
    #     self.name = self.name.upper()
    #     super(Designation, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'designation'

class Division(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    # def save(self, *args, **kwargs):
    #     self.name = self.name.title()
    #     super(Division, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'division'

class SubDivision(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super(SubDivision, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'subdivision'

class Shopfloor(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super(Shopfloor, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'shopfloor'


class Shift(models.Model):
    name = models.CharField(max_length=100)
    shift_id = models.CharField(max_length=10, blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    tolerance_before_start_time = models.DurationField(blank=True, null=True)
    tolerance_after_start_time = models.DurationField(blank=True, null=True)
    tolerance_before_end_time = models.DurationField(blank=True, null=True)
    tolerance_after_end_time = models.DurationField(blank=True, null=True)
    grace_period_at_start_time = models.DurationField(blank=True, null=True)
    grace_period_at_end_time = models.DurationField(blank=True, null=True)
    absent_threshold = models.DurationField(blank=True, null=True)
    half_day_threshold = models.DurationField(blank=True, null=True)
    full_day_threshold = models.DurationField(blank=True, null=True)    
    overtime_threshold_before_start = models.DurationField(blank=True, null=True)  
    overtime_threshold_after_end = models.DurationField(blank=True, null=True) 
    lunch_in = models.TimeField(blank=True, null=True)
    lunch_out = models.TimeField(blank=True, null=True)
    lunch_duration = models.DurationField(blank=True, null=True)
    night_shift = models.BooleanField(default=False)
    include_lunch_break_in_half_day = models.BooleanField(default=False)
    include_lunch_break_in_full_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_night_shift(self):
        if self.start_time > self.end_time:
            return True
        return False

    def calculate_lunch_duration(self):
        return self.lunch_out - self.lunch_in

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(Shift, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'shift'

class AttendanceCorrectionConfig(models.Model):
    id = models.AutoField(primary_key=True)
    is_enabled = models.BooleanField(default=True, help_text="Enable or disable the auto-correction feature")
    cutoff_time = models.TimeField(default=datetime.time(6, 0, 0), help_text="Time threshold to determine if the current day should be considered or shifted to the previous day")

    class Meta:
        db_table = "attendance_correction_config"

    @classmethod
    def load(cls):
        """Get or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        """Ensure only one record exists by forcing the primary key to 1"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton instance"""
        pass

    def __str__(self):
        return f"Correction Enabled: {self.is_enabled}, Cutoff Time: {self.cutoff_time}"