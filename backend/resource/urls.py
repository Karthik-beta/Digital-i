from django.urls import re_path, path
from resource.views import (
                            EmployeeListCreate, EmployeeRetrieveUpdateDestroy, EmployeeIdGet, 
                            AttendanceListCreate, ExportAttendanceExcelView, AttendanceMetricsAPIView,
                            AttendanceMonthlyMetricsAPIView, LogsListCreate, LogsRetrieveUpdateDestroy,
                            EmployeeDropdownList, ExportEmployeeAttendanceExcelView, ExportAllEmployeeAttendanceExcelView, 
                            LastLogIdView, MandaysAttendanceListCreate, ManDaysAttendanceExcelExport, ManDaysWorkedExcelExport,
                            ManDaysMissedPunchExcelExport,ExportLogsExcelView, ResetMandaysView, test_view, ExportMonthlyDutyHourExcel, 
                            ExportAllEmployeeAttendanceExcelView2, ExportMonthlyMusterRoleExcel, ExportMonthlyPayrollExcel, ExportMonthlyShiftRoasterExcel,
                            ExportMonthlyOvertimeExcel, ExportMonthlyLateEntryExcel, ExportMonthlyEarlyExitExcel, ExportMonthlyAbsentExcel, ExportMonthlyPresentExcel, ProcessLogView,
                            ExportMonthlyOvertimeExcel2, ExportMonthlyLateEntryExcel2, ExportMonthlyEarlyExitExcel2, ExportMonthlyAbsentExcel2, ExportMonthlyPresentExcel2,
                            ExportMonthlyShiftRoasterExcel2, ExportMonthlyPayrollExcel2, ExportMonthlyMusterRoleExcel2, ExportMonthlyOvertimeRoundoffExcel2, OvertimeRoundoffRulesView, 
                            OvertimeRoundoffRulesUpdate, MonthlyAttendanceView, UpdateAttendanceView, HolidayListCreate, HolidayRetrieveUpdateDestroy, AttendanceStatsView, EmployeeStatisticsAPI,
                            ExternalDatabaseCredentialView, ExternalDatabaseCredentialUpdateView, TestConnectionAPIView, BiometricDeviceConfigurationListAPIView, BiometricDeviceConfigurationUpdateDestroy, ResetAttendanceView,
                            RecalculateAttendanceView)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    re_path(r'^unique_id/$', EmployeeIdGet.as_view(), name='employee-options-list'),
    
    re_path(r'^employee/$', EmployeeListCreate.as_view(), name='employee-list-create'),
    re_path(r'^employee/(?P<id>\d+)/$', EmployeeRetrieveUpdateDestroy.as_view(), name='employee-retrieve-update-destroy'),
    re_path(r'^employee/options/$', EmployeeRetrieveUpdateDestroy.as_view(), name='employee-retrieve-update-destroy'),

    re_path(r'^attendance/$', AttendanceListCreate.as_view(), name='attendance-list-create'),

    re_path(r'^attendance/export/$', ExportAttendanceExcelView.as_view(), name='attendance-export'),

    re_path(r'^attendance/metrics/daily/$', AttendanceMetricsAPIView.as_view(), name='attendance-metrics-daily'),

    re_path(r'^attendance/metrics/monthly/$', AttendanceMonthlyMetricsAPIView.as_view(), name='attendance-metrics-monthly'),

    re_path(r'^logs/$', LogsListCreate.as_view(), name='logs-list-create'),
    re_path(r'^logs/(?P<id>\d+)/$', LogsRetrieveUpdateDestroy.as_view(), name='logs-list-create'),

    re_path(r'^employee/dropdown/$', EmployeeDropdownList.as_view(), name='employee-dropdown-list'),

    re_path(r'^attendance/employee/$', ExportEmployeeAttendanceExcelView.as_view()),

    re_path(r'^attendance/export/allemployees/$', ExportAllEmployeeAttendanceExcelView.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_movements/$', ExportAllEmployeeAttendanceExcelView2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_duty_hours/$', ExportMonthlyDutyHourExcel.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_muster_role/$', ExportMonthlyMusterRoleExcel2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_payroll/$', ExportMonthlyPayrollExcel2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_shift_roaster/$', ExportMonthlyShiftRoasterExcel2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_overtime/$', ExportMonthlyOvertimeExcel2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_roundoff_overtime/$', ExportMonthlyOvertimeRoundoffExcel2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_late_entry/$', ExportMonthlyLateEntryExcel2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_early_exit/$', ExportMonthlyEarlyExitExcel2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_absent/$', ExportMonthlyAbsentExcel2.as_view(), name='attendance-export'),

    re_path(r'^attendance/export/monthly_present/$', ExportMonthlyPresentExcel2.as_view(), name='attendance-export'),

    re_path(r'^last_log_id/$', LastLogIdView.as_view(), name='attendance-export'),

    re_path(r'^attendance/mandays/$', MandaysAttendanceListCreate.as_view(), name='logs-list-create'),

    re_path(r'^attendance/mandays/report/$', ManDaysAttendanceExcelExport.as_view(), name='logs-list-create'),

    re_path(r'^attendance/mandays/work_report/$', ManDaysWorkedExcelExport.as_view(), name='logs-list-create'),

    re_path(r'^attendance/mandays/missed_punch_report/$', ManDaysMissedPunchExcelExport.as_view(), name='logs-list-create'),

    re_path(r'^logs/export/$', ExportLogsExcelView.as_view(), name='logs-export'),

    re_path(r'^attendance/reset/$', ResetAttendanceView.as_view(), name='attendance-reset'),

    re_path(r'^attendance/mandays/reset/$', ResetMandaysView.as_view(), name='logs-list-create'),

    re_path(r'^test/$', test_view.as_view(), name='logs-list-create'),

    re_path(r'^manual_log/$', ProcessLogView.as_view(), name='process-log'),

    re_path(r'^overtime_rules/$', OvertimeRoundoffRulesView.as_view(), name='overtime-rules'),
    re_path(r'^overtime_rules/(?P<id>\d+)/$', OvertimeRoundoffRulesUpdate.as_view(), name='overtime-rules-update'),

    re_path(r'^attendance/monthly_overview/$', MonthlyAttendanceView.as_view(), name='monthly-attendance'),
    re_path(r'^attendance/monthly_overview/(?P<attendance_id>\d+)/$', UpdateAttendanceView.as_view(), name='monthly-attendance'),

    re_path(r'^holiday_list/$', HolidayListCreate.as_view(), name='holiday-list-create'),
    re_path(r'^holiday_list/(?P<id>\d+)/$', HolidayRetrieveUpdateDestroy.as_view(), name='holiday-list-create'),

    re_path(r'^attendance/stats/$', AttendanceStatsView.as_view(), name='attendance-stats'),

    re_path(r'^employee/stats/$', EmployeeStatisticsAPI.as_view(), name='employee-statistics'),

    path('database_credential/', ExternalDatabaseCredentialView.as_view(), name='database-credentials-list'),
    path('database_credential/update/', ExternalDatabaseCredentialUpdateView.as_view(), name='database-credentials-update'),

    path('test_connection/', TestConnectionAPIView.as_view(), name='check-database-connection'),

    re_path(r'^biometric_device_config/$', BiometricDeviceConfigurationListAPIView.as_view(), name='Biometric-Devices-Details'),
    re_path(r'^biometric_device_config/(?P<id>\d+)/$', BiometricDeviceConfigurationUpdateDestroy.as_view(), name='Biometric-Devices-Update-Delete'),

    re_path(r'^attendance/recalculate/$', RecalculateAttendanceView.as_view(), name='attendance-recalculate')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

