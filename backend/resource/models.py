from django.db import models
import datetime
from django.core.exceptions import ValidationError

class Employee(models.Model):

    BANK_ACCOUNT_CHOICES = (
        ('Savings Account', 'Savings Account'),
        ('Current Account', 'Current Account'),
        ('Salary Account', 'Salary Account'),
        ('NRI Account', 'NRI Account'),
        ('Pension Account', 'Pension Account'),
        ('Other Account', 'Other Account'),
    )

    CATEGORY_CHOICES = (
        ('Permanent Employee', 'Permanent Employee'),
        ('Temporary Employee', 'Temporary Employee'),
        ('Contractor Employee', 'Contractor Employee'),
        ('Probation Employee', 'Probation Employee'),
    )

    JOB_TYPE_CHOICES = (
        ('Training', 'Training'),
        ('Confirmed', 'Confirmed'),
        ('Professional', 'Professional'),
        ('Temporary', 'Temporary'),
        ('Permanent', 'Permanent'),
    )

    JOB_STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Resigned', 'Resigned'),
        ('Absconded', 'Absconded'),
    )

    MARITAL_STATUS_CHOICES = (
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    )

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    COURSE_TYPE_CHOICES = (
        ('Under Graduate', 'Under Graduate'),
        ('Post Graduate', 'Post Graduate'),
        ('Diploma', 'Diploma'),
        ('Certificate', 'Certificate'),
        ('Other', 'Other'),
    )

    SHIFT_CHOICES = (
        ('GS', 'General Shift'),
        ('Day Shift', 'Day Shift'),
        ('Night Shift', 'Night Shift'),
        ('Rotational Shift', 'Rotational Shift'),
        ('Split Shift', 'Split Shift'),
        ('Flexi Shift', 'Flexi Shift'),
        ('Other Shift', 'Other Shift'),
    )

    WEEK_DAYS_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    )
    
    id = models.AutoField(primary_key=True)
    profile_pic = models.ImageField(default="profile_pics/default_pic.jpg",upload_to='profile_pics/', blank=True, null=True)
    employee_id = models.CharField(max_length=20, unique=True)
    employee_name = models.CharField(max_length=100)
    device_enroll_id = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_no = models.PositiveBigIntegerField(blank=True, null=True)
    pf_no = models.CharField(max_length=20, blank=True, null=True)
    esi_no = models.CharField(max_length=20, blank=True, null=True)
    insurance_no = models.CharField(max_length=20, blank=True, null=True)
    # ar_no = models.CharField(max_length=20, blank=True, null=True)
    # ap_no = models.CharField(max_length=20, blank=True, null=True)
    # cn_no = models.CharField(max_length=20, blank=True, null=True)


    # Bank Details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=True, null=True)
    bank_account_no = models.CharField(max_length=20, blank=True, null=True)
    bank_account_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_type = models.CharField(max_length=20, choices=BANK_ACCOUNT_CHOICES, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    # Official Details
    company = models.ForeignKey('config.Company', on_delete=models.SET_NULL, blank=True, null=True)
    location = models.ForeignKey('config.Location', on_delete=models.SET_NULL, blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True, null=True)
    department = models.ForeignKey('config.Department', on_delete=models.SET_NULL, blank=True, null=True)
    designation = models.ForeignKey('config.Designation', on_delete=models.SET_NULL, blank=True, null=True)
    division = models.ForeignKey('config.Division', on_delete=models.SET_NULL, blank=True, null=True)
    subdivision = models.ForeignKey('config.SubDivision', on_delete=models.SET_NULL, blank=True, null=True)
    shopfloor = models.ForeignKey('config.Shopfloor', on_delete=models.SET_NULL, blank=True, null=True)
    job_type = models.CharField(max_length=100, choices= JOB_TYPE_CHOICES, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    date_of_leaving = models.DateField(blank=True, null=True)
    job_status = models.CharField(max_length=100, choices=JOB_STATUS_CHOICES, blank=True, null=True)
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='reports', blank=True, null=True)
    alt_reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='alt_reports',blank=True, null=True)
    reason_for_leaving = models.TextField(blank=True, null=True)
 
    # Personal Details
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_no = models.PositiveBigIntegerField(blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    country_name = models.CharField(max_length=100, default="India", blank=True, null=True)
    country_code = models.CharField(max_length=10, default="IN", blank=True, null=True)
    uid_no = models.CharField(max_length=20, blank=True, null=True) #aadhar 
    pan_no = models.CharField(max_length=20, blank=True, null=True)
    voter_id = models.CharField(max_length=20, blank=True, null=True)
    driving_license = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    present_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)

    # Qualifications
    graduation = models.CharField(max_length=100, blank=True, null=True)
    course_type = models.CharField(max_length=100, choices=COURSE_TYPE_CHOICES, blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    place_of_graduation = models.CharField(max_length=100, blank=True, null=True)
    aggregate = models.FloatField(blank=True, null=True)
    year_of_graduation = models.PositiveIntegerField(blank=True, null=True)

    # Work Configuration
    # Weekly Off and Shifts
    shift = models.ForeignKey('config.Shift', on_delete=models.SET_NULL, blank=True, null=True)
    auto_shift = models.BooleanField(default=False)
    first_weekly_off = models.IntegerField(default=6, choices=WEEK_DAYS_CHOICES, blank=True, null=True)
    second_weekly_off = models.IntegerField(default=6, choices=WEEK_DAYS_CHOICES, blank=True, null=True)
    week_off_effective_date = models.DateField(blank=True, null=True)

    # Late/Early/Overtime/Flexi Time Marking
    flexi_time = models.BooleanField(default=False)
    consider_late_entry = models.BooleanField(default=False)
    consider_early_exit = models.BooleanField(default=False)
    consider_extra_hours_worked = models.BooleanField(default=False)
    consider_late_entry_on_holiday = models.BooleanField(default=False)
    consider_early_exit_on_holiday = models.BooleanField(default=False)
    consider_extra_hours_worked_on_holiday = models.BooleanField(default=False)

    consider_fixed_shift = models.BooleanField(default=False)
    consider_first_weekly_off = models.BooleanField(default=False)
    consider_second_weekly_off = models.BooleanField(default=False)

    # Punch Out Setting
    search_next_day = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.employee_name
    
    def save(self, *args, **kwargs):
        if self.employee_name is not None:
            self.employee_name = self.employee_name.title()

        if self.device_enroll_id is not None:
            self.device_enroll_id = self.device_enroll_id.upper()

        if self.email is not None:
            self.email = self.email.lower()

        if self.bank_name is not None:
            self.bank_name = self.bank_name.title()

        if self.bank_branch is not None:
            self.bank_branch = self.bank_branch.title()

        if self.emergency_contact_name is not None:
            self.emergency_contact_name = self.emergency_contact_name.title()

        if self.spouse_name is not None:
            self.spouse_name = self.spouse_name.title()

        if self.blood_group is not None:
            self.blood_group = self.blood_group.upper()

        if self.country_name is not None:
            self.country_name = self.country_name.title()

        if self.graduation is not None:
            self.graduation = self.graduation.title()

        if self.course is not None:
            self.course = self.course.title()

        if self.place_of_graduation is not None:
            self.place_of_graduation = self.place_of_graduation.title()

        super(Employee, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.profile_pic.delete()
        super(Employee, self).delete(*args, **kwargs)

    


    class Meta:
        ordering = ['id']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        db_table = 'employee'
        indexes = [
            models.Index(fields=['employee_id'], name='idx_employee_id'),

            # Composite indexes
            models.Index(fields=['employee_id', 'employee_name'], name='idx_employee_id_name'),
            models.Index(fields=['bank_account_no', 'bank_name'], name='idx_bank_account_bank_name'),
            models.Index(fields=['job_type', 'job_status'], name='idx_job_type_status'),
            models.Index(fields=['date_of_joining', 'date_of_leaving'], name='idx_joining_leaving'),

            # Add more indexes as needed
        ]

class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    employeeid = models.CharField(max_length=50, blank=True, null=True)
    log_datetime = models.DateTimeField(blank=True, null=True)
    direction = models.CharField(max_length=50, blank=True, null=True)
    shortname = models.CharField(max_length=50, blank=True, null=True)
    serialno = models.CharField(max_length=50, blank=True, null=True) 

    class Meta:   
        db_table = 'logs'
        indexes = [
            models.Index(fields=['employeeid', 'log_datetime'], name='logs_emp_logdt'), # Composite index
            models.Index(fields=['log_datetime'], name='logs_logdt'),
            models.Index(fields=['direction'], name='logs_dir'),  
        ]

class ProcessedLogs(models.Model):
    id = models.IntegerField(primary_key=True)
    employeeid = models.CharField(max_length=50, blank=True, null=True)
    log_datetime = models.DateTimeField(blank=True, null=True)
    direction = models.CharField(max_length=50, blank=True, null=True)
    shortname = models.CharField(max_length=50, blank=True, null=True)
    serialno = models.CharField(max_length=50, blank=True, null=True) 

    class Meta:   
        db_table = 'processed_logs'
        indexes = [
            models.Index(fields=['id'], name='processedlogs_id'), # Single index on id
            models.Index(fields=['employeeid', 'log_datetime'], name='processed_emp_logdt'), # Composite index
            models.Index(fields=['log_datetime'], name='processed_logdt'),
            models.Index(fields=['direction'], name='processed_dir'),  
        ]
        
class LastLogId(models.Model):
    last_log_id = models.IntegerField(default=0, editable=True)
    
    class Meta:
        db_table = 'last_log_id'        

class LastLogIdMandays(models.Model):
    last_log_id = models.IntegerField(default=0, editable=True)
    
    class Meta:
        db_table = 'last_log_id_mandays'

class Attendance(models.Model):
    employeeid = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    logdate = models.DateField()
    first_logtime = models.DateTimeField(blank=True, null=True)
    last_logtime = models.DateTimeField(blank=True, null=True)
    in_direction = models.CharField(max_length=50, blank=True, null=True)
    out_direction = models.CharField(max_length=50, blank=True, null=True)
    in_shortname = models.CharField(max_length=50, blank=True, null=True)
    out_shortname = models.CharField(max_length=50, blank=True, null=True)
    total_time = models.DurationField(blank=True, null=True)
    late_entry = models.DurationField(blank=True, null=True, default=None)
    early_exit = models.DurationField(blank=True, null=True, default=None)
    overtime = models.DurationField(blank=True, null=True, default=None)
    shift = models.CharField(max_length=50, blank=True, null=True)
    shift_status = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        unique_together = ['employeeid', 'logdate']
        db_table = 'attendance'
        indexes = [
            models.Index(fields=['logdate'], name='idx_logdate'),  # Single index on logdate
            models.Index(fields=['employeeid', 'logdate'], name='idx_employeeid_logdate'),  # Composite index
        ]
    
    # def save(self, *args, **kwargs):
    #     # Check and replace "00:00:00" with null for specified fields
    #     fields_to_replace = ['late_entry', 'early_exit', 'overtime']
    #     for field_name in fields_to_replace:
    #         field_value = getattr(self, field_name)
    #         if field_value == datetime.time(0, 0):
    #             setattr(self, field_name, None)
        
    #     super(Attendance, self).save(*args, **kwargs)

class OvertimeRoundoffRules(models.Model):
    id = models.AutoField(primary_key=True)
    round_off_interval = models.DurationField(default=datetime.timedelta(minutes=15))
    round_off_direction = models.CharField(
        max_length=50, 
        default='nearest', 
        choices=(('Up', 'Up'), ('Down', 'Down'), ('Nearest', 'Nearest'))
    )

    class Meta:
        db_table = 'overtime_roundoff_rules'

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

class ManDaysAttendance(models.Model):
    employeeid = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    shift = models.CharField(max_length=50, blank=True, null=True)
    shift_status = models.CharField(max_length=50, blank=True, null=True)
    logdate = models.DateField()
    duty_in_1 = models.TimeField(blank=True, null=True)
    duty_out_1 = models.TimeField(blank=True, null=True)
    total_time_1 = models.DurationField(blank=True, null=True)
    duty_in_2 = models.TimeField(blank=True, null=True)
    duty_out_2 = models.TimeField(blank=True, null=True)
    total_time_2 = models.DurationField(blank=True, null=True)
    duty_in_3 = models.TimeField(blank=True, null=True)
    duty_out_3 = models.TimeField(blank=True, null=True)
    total_time_3 = models.DurationField(blank=True, null=True)
    duty_in_4 = models.TimeField(blank=True, null=True)
    duty_out_4 = models.TimeField(blank=True, null=True)
    total_time_4 = models.DurationField(blank=True, null=True)
    duty_in_5 = models.TimeField(blank=True, null=True)
    duty_out_5 = models.TimeField(blank=True, null=True)
    total_time_5 = models.DurationField(blank=True, null=True)
    duty_in_6 = models.TimeField(blank=True, null=True)
    duty_out_6 = models.TimeField(blank=True, null=True)
    total_time_6 = models.DurationField(blank=True, null=True)
    duty_in_7 = models.TimeField(blank=True, null=True)
    duty_out_7 = models.TimeField(blank=True, null=True)
    total_time_7 = models.DurationField(blank=True, null=True)
    duty_in_8 = models.TimeField(blank=True, null=True)
    duty_out_8 = models.TimeField(blank=True, null=True)
    total_time_8 = models.DurationField(blank=True, null=True)
    duty_in_9 = models.TimeField(blank=True, null=True)
    duty_out_9 = models.TimeField(blank=True, null=True)
    total_time_9 = models.DurationField(blank=True, null=True)
    duty_in_10 = models.TimeField(blank=True, null=True)
    duty_out_10 = models.TimeField(blank=True, null=True)
    total_time_10 = models.DurationField(blank=True, null=True)
    total_hours_worked = models.DurationField(blank=True, null=True)

    class Meta:
        unique_together = ['employeeid', 'logdate']
        db_table = 'mandays_attendance'

class ManDaysMissedPunchAttendance(models.Model):
    employeeid = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    shift = models.CharField(max_length=50, blank=True, null=True)
    shift_status = models.CharField(max_length=50, blank=True, null=True)
    logdate = models.DateField()
    duty_in_1 = models.TimeField(blank=True, null=True)
    duty_out_1 = models.TimeField(blank=True, null=True)
    duty_in_2 = models.TimeField(blank=True, null=True)
    duty_out_2 = models.TimeField(blank=True, null=True)
    duty_in_3 = models.TimeField(blank=True, null=True)
    duty_out_3 = models.TimeField(blank=True, null=True)
    duty_in_4 = models.TimeField(blank=True, null=True)
    duty_out_4 = models.TimeField(blank=True, null=True)
    duty_in_5 = models.TimeField(blank=True, null=True)
    duty_out_5 = models.TimeField(blank=True, null=True)
    duty_in_6 = models.TimeField(blank=True, null=True)
    duty_out_6 = models.TimeField(blank=True, null=True)
    duty_in_7 = models.TimeField(blank=True, null=True)
    duty_out_7 = models.TimeField(blank=True, null=True)
    duty_in_8 = models.TimeField(blank=True, null=True)
    duty_out_8 = models.TimeField(blank=True, null=True)
    duty_in_9 = models.TimeField(blank=True, null=True)
    duty_out_9 = models.TimeField(blank=True, null=True)
    duty_in_10 = models.TimeField(blank=True, null=True)
    duty_out_10 = models.TimeField(blank=True, null=True)

    class Meta:
        db_table = 'mandays_missed_punch_attendance'

class ManualLogs(models.Model):
    employeeid = models.CharField(max_length=50, blank=True, null=True)
    log_datetime = models.DateTimeField(blank=True, null=True)
    direction = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'manual_logs'
        indexes = [
             models.Index(fields=['employeeid', 'log_datetime'], name='manual_emp_logdt'),
            models.Index(fields=['log_datetime'], name='manual_logdt'),
            models.Index(fields=['direction'], name='manual_dir'),
        ]

class HolidayList(models.Model):
    holiday_date = models.DateField()
    holiday_name = models.CharField(max_length=100)
    holiday_type = models.CharField(choices=(('PH', 'PH'), ('FH', 'FH')), default='PH', max_length=10)
    holiday_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'holiday_list'
        indexes = [
            models.Index(fields=['holiday_date'], name='idx_holiday_date'),  # Single index on holiday_date
            models.Index(fields=['holiday_name'], name='idx_holiday_name'),  # Single index on holiday_name
            models.Index(fields=['holiday_type'], name='idx_holiday_type'),  # Single index on holiday_type
            models.Index(fields=['holiday_date', 'holiday_name'], name='idx_holiday_date_name'),  # Composite index
        ]

class AWOWorkOffCorrection(models.Model):
    """
    Model to store records of 'WO' statuses corrected to 'A' due to the 'A-WO-A' pattern.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    corrected_date = models.DateField(db_index=True)  # The 'WO' date that was corrected to 'A'
    day1_date = models.DateField()  # Date of the preceding 'A'
    day3_date = models.DateField()  # Date of the succeeding 'A'
    original_status = models.CharField(max_length=50, default='WO') # Store original status for clarity
    correction_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'awo_work_off_corrections'
        unique_together = ('employee', 'corrected_date')

    def __str__(self):
        return f"Correction for {self.employee.employee_id} on {self.corrected_date}"

class ExternalDatabaseCredential(models.Model):
    """
    Model to store external database credentials to import logs data.
    """

    DATABASE_TYPE_CHOICES = (
        ('MS_SQL', 'MS_SQL'),
        ('POSTGRESQL', 'POSTGRESQL')
    )

    database_type = models.CharField(max_length=40, choices=DATABASE_TYPE_CHOICES, help_text="The type of external database (e.g., MSSQL, PostgreSQL).")
    name = models.CharField(max_length=256)
    user = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    host = models.CharField(max_length=256)
    port = models.IntegerField()

    table_name = models.CharField(max_length=256)
    id_field = models.CharField(max_length=256)
    employeeid_field = models.CharField(max_length=256)
    direction_field = models.CharField(max_length=256)
    shortname_field = models.CharField(max_length=256)
    serialno_field = models.CharField(max_length=256)
    log_datetime_field = models.CharField(max_length=256)

    class Meta:
        db_table = 'database_credentials'

    def save(self, *args, **kwargs):
        """
        Enforce that only one record can exist in the table.
        If a record already exists, it will update the existing one instead of creating a new one.
        """
        if not self.pk and ExternalDatabaseCredential.objects.exists():
            raise ValidationError("Only one record is allowed in the ExternalDatabaseCredential table.")
        
        super(ExternalDatabaseCredential, self).save(*args, **kwargs)

    def __str__(self):
        return f"External Database Credential for {self.database_type} - {self.name}"

class BiometricDeviceConfiguration(models.Model):
    """
    Model representing the configuration of a biometric device.
    This model stores information such as the device's location, direction, 
    serial number, and related company details.
    """
    
    DEVICE_DIRECTION_CHOICES = (
        ('IN', 'IN'),
        ('OUT', 'OUT'),
        ('BOTH', 'BOTH')
    )
    
    company = models.ForeignKey('config.Company', on_delete=models.SET_NULL, blank=True, null=True, help_text="Reference to the company associated with the biometric device.")
    location = models.ForeignKey('config.Location', on_delete=models.SET_NULL, blank=True, null=True, help_text="Reference to the location where the biometric device is installed.")
    device_no = models.CharField(max_length=256, blank=True, null=True, help_text="Unique identifier for the device.")
    serial_number = models.CharField(max_length=256, blank=True, null=True, help_text="Serial number of the biometric device.")
    direction_of_use = models.CharField(max_length=12, choices=DEVICE_DIRECTION_CHOICES, help_text="Indicates the direction of access (IN, OUT, or BOTH) the device is configured for.")
    purpose_of_device = models.CharField(max_length=256, blank=True, null=True, help_text="Describes the intended purpose of the biometric device (e.g., attendance, security).")
    ip_address = models.CharField(max_length=256, blank=True, null=True, help_text="IP address of the biometric device for network communication.")
    
    class Meta:
        db_table = 'biometric_devices'
        verbose_name = "Biometric Device Configuration"
        verbose_name_plural = "Biometric Device Configurations"

class AllLogs(models.Model):
    id = models.AutoField(primary_key=True)
    employeeid = models.CharField(max_length=50, blank=True, null=True)
    log_datetime = models.DateTimeField(blank=True, null=True)
    direction = models.CharField(max_length=50, blank=True, null=True)
    shortname = models.CharField(max_length=50, blank=True, null=True)
    serialno = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=50, blank=True, null=True)  

    class Meta:
        db_table = 'all_logs'
        unique_together = ['employeeid', 'log_datetime', 'direction', 'source']
        indexes = [
            models.Index(fields=['employeeid', 'log_datetime'], name='all_emp_logdt'), # Composite index
            models.Index(fields=['log_datetime'], name='all_logdt'),
            models.Index(fields=['direction'], name='all_dir'),  
        ]