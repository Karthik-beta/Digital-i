import { Component, OnInit, ViewChild } from '@angular/core';
import { Table } from 'primeng/table';
import { MenuItem } from 'primeng/api';
import { SharedService } from 'src/app/shared.service';
import { MessageService } from 'primeng/api';
import { LazyLoadEvent } from 'primeng/api';
import { debounceTime, distinctUntilChanged, startWith, switchMap, timeout, catchError } from 'rxjs/operators';
import { Observable, Subscription, interval, timer } from 'rxjs';
import { of } from 'rxjs';

interface Employee {
    employee_id: string;
}

interface Location {
    name: string;
}

interface Company {
    name: string;
}

interface Department {
    name: string;
}

interface Designation {
    name: string;
}

interface Criteria {
    name: string;
    code: string;
    command: () => void;
}

@Component({
  selector: 'app-monthly-in-out',
  templateUrl: './monthly-in-out.component.html',
  styleUrl: './monthly-in-out.component.scss'
})
export class MonthlyInOutComponent implements OnInit {

    @ViewChild('dt') dt: Table;

    reportList: any;

    metrics: any;

    date: Date;

    rangeDates: Date[];

    metricsDate = [];

    metricsPresent = [];

    metricsAbsent = [];

    metricsLateEntry = [];

    metricsEarlyExit = [];

    metricsOvertime = [];

    data: any;

    options: any;

    totalRecords: number = 0;

    rowsPerPageOptions: number[] = [10, 20, 30];

    rows: number = 10;

    currentPage: number = 1;

    loading: boolean = false;

    searchQuery: string = '';

    company_name: string = '';

    location_name: string = '';

    shift_status: string = '';

    late_entry: boolean = false;

    early_exit: boolean = false;

    overtime: boolean = false;

    missed_punch: boolean = false;

    insufficient_duty_hours: boolean = false;

    companies: any[] = [];

    locations: any[] = [];

    selectedCompany: any;

    selectedLocation: any;

    showElements: string = 'true';

    items: MenuItem[] = [];

    visible: boolean = false;

    position: string = 'top';

    employeeList: any[] = [];

    employee_id: any;

    selectedMonth: any;

    selectedYear: any;

    department_names: string[] = [];

    designation_names: string[] = [];

    selectedEmployee: Employee[] = [];

    selectedLocations: Location[] = [];

    selectedCompanies: Company[] = [];

    selectedEmplyees: Employee[] = [];

    selectedDepartments: Department[] = [];

    selectedDesignations: Designation[] = [];

    employee_ids: string[] = [];

    location_names: string[] = [];

    company_names: string[] = [];

    month: Date[];

    criteria: Criteria[] | undefined;

    report_status: string = '';

    constructor(
        private service: SharedService,
        private messageService: MessageService,
    ) { }

    ngOnInit() {

        this.items = [
            { label: 'Import', icon: 'fas fa-file-import' },
            { label: 'Export', icon: 'fas fa-download', command: () => this.openExportModal() },
        ];

        this.criteria = [
            { name: 'Monthly Movements Register', code: 'monthly_movements', command: () => this.setReportStatus('monthly_movements') },
            { name: 'In-Out Movements Register', code: 'allemployees', command: () => this.setReportStatus('allemployees')},
            { name: 'Duty Hours Register', code: 'monthly_duty_hours', command: () => this.setReportStatus('monthly_duty_hours') },
            { name: 'Musterrole Register', code: 'monthly_muster_role', command: () => this.setReportStatus('monthly_muster_role') },
            { name: 'Payroll Register', code: 'monthly_payroll', command: () => this.setReportStatus('monthly_payroll') },
            { name: 'Shift Roaster Register', code: 'monthly_shift_roaster', command: () => this.setReportStatus('monthly_shift_roaster') },
            { name: 'Overtime Register', code: 'monthly_overtime', command: () => this.setReportStatus('monthly_overtime')},
            { name: 'Overtime Roundoff Register', code: 'monthly_overtime_roundoff', command: () => this.setReportStatus('monthly_roundoff_overtime')},
            { name: 'Late Entry Register', code: 'monthly_late_entry', command: () => this.setReportStatus('monthly_late_entry')},
            { name: 'Early Exit Register', code: 'monthly_early_exit', command: () => this.setReportStatus('monthly_early_exit')},
            { name: 'Absent Register', code: 'monthly_absent', command: () => this.setReportStatus('monthly_absent')},
            { name: 'Present Register', code: 'monthly_present', command: () => this.setReportStatus('monthly_present')},
        ];

        this.initCharts();
        this.getAttendanceMonthlyMetrics();
        this.getCompaniesList();
        this.getLocationsList();
        this.getEmployeeList();
    }

    initCharts() {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
        const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

        this.data = {
            labels: this.metricsDate,
            datasets: [
                {
                    label: 'Present',
                    backgroundColor: documentStyle.getPropertyValue('--green-500'),
                    borderColor: documentStyle.getPropertyValue('--green-500'),
                    data: this.metricsPresent
                },
                {
                    label: 'Absent',
                    backgroundColor: documentStyle.getPropertyValue('--red-500'),
                    borderColor: documentStyle.getPropertyValue('--red-500'),
                    data: this.metricsAbsent
                },
                {
                    label: 'Late Entry',
                    backgroundColor: documentStyle.getPropertyValue('--indigo-400'),
                    borderColor: documentStyle.getPropertyValue('--indigo-400'),
                    data: this.metricsLateEntry
                },
                {
                    label: 'Early Exit',
                    backgroundColor: documentStyle.getPropertyValue('--teal-400'),
                    borderColor: documentStyle.getPropertyValue('--teal-400'),
                    data: this.metricsEarlyExit
                },
                {
                    label: 'Overtime',
                    backgroundColor: documentStyle.getPropertyValue('--purple-400'),
                    borderColor: documentStyle.getPropertyValue('--purple-400'),
                    data: this.metricsOvertime
                }
            ]
        };

        this.options = {
            maintainAspectRatio: false,
            aspectRatio: 1.5,
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        color: textColorSecondary,
                        font: {
                            weight: 500
                        }
                    },
                    grid: {
                        color: surfaceBorder,
                        drawBorder: false
                    }
                },
                y: {
                    stacked: true,
                    ticks: {
                        color: textColorSecondary
                    },
                    grid: {
                        color: surfaceBorder,
                        drawBorder: false
                    }
                }

            }
        };
    }

    getAttendanceReport(event: LazyLoadEvent) {
        this.loading = true;

        const params: any = {
            page: ((event.first || 0 ) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: event.sortField || '',
            ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
            search: this.searchQuery || '',
            logdate: this.date || '',
            shift_status: this.shift_status || '',
            late_entry: this.late_entry || false,
            early_exit: this.early_exit || false,
            overtime: this.overtime || false,
            missed_punch: this.missed_punch || false,
            insufficient_duty_hours: this.insufficient_duty_hours || false,
            employee_ids: this.employee_ids.join(','),
            company_name: this.company_names.join(','),
            location_name: this.location_names.join(','),
            department_name: this.department_names.join(','),
            designation_name: this.designation_names.join(','),
        };

        if (this.rangeDates && this.rangeDates.length === 2 && this.rangeDates[0] && this.rangeDates[1]) {
            params.date_from = this.formatDate(this.rangeDates[0]);
            params.date_to = this.formatDate(this.rangeDates[1]);
        }

        // this.service.getAttendanceList(params).subscribe((data: any) => {
        //     this.reportList = data.results;
        //     this.totalRecords = data.count;
        //     this.loading = false;
        // });
        this.service.getAttendanceList(params).pipe(
            timeout(10000), // Set timeout to 10 seconds
            catchError(error => {
                console.error('Request timed out or failed', error);
                this.loading = false;
                return of({ results: [], count: 0 }); // Return an empty result set in case of error
            })
        ).subscribe((data: any) => {
            this.reportList = data.results;
            this.totalRecords = data.count;
            this.loading = false;
        });
    }

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    onDateChange(query: Date): void {
        const formattedDate = this.formatDate(query);
        this.searchQuery = formattedDate;
        this.dt.filterGlobal(formattedDate, 'contains');
    }

    onCriteriaChange(event: any) {
        const selectedCriteria = event.value;
        if (selectedCriteria && selectedCriteria.command) {
            selectedCriteria.command();
        }
    }

    searchAttendance(criteria: string): void {
        // Set the searchQuery to the criteria you want to search, in this case 'P'
        this.shift_status = criteria;

        // Reset all flags to false initially
        this.late_entry = false;
        this.early_exit = false;
        this.overtime = false;
        this.missed_punch = false;
        this.insufficient_duty_hours = false;

        // Perform the search
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    performAttendanceAction(actionType: string) {
        const params: any = {
            month: this.selectedMonth || '',
            year: this.selectedYear || '',
            actionType: actionType, // Include the actionType in the parameters
        };
    }

    setReportStatus(status: string) {
        this.report_status = status;
    }

    onDateRangeChange(event: any) {
        if (this.rangeDates && this.rangeDates.length === 2 && this.rangeDates[0] && this.rangeDates[1]) {
            const params: any = {
                page: ((event.first || 0 ) / (event.rows || 5) + 1).toString(),
                page_size: (event.rows || 10).toString(),
                sortField: event.sortField || '',
                ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
                date_from: this.formatDate(this.rangeDates[0]),
                date_to: this.formatDate(this.rangeDates[1]),
            };
          this.getAttendanceReport(params);
        }
    }

    // formatDate(date: Date): string {
    //     const year = date.getFullYear();
    //     const month = ('0' + (date.getMonth() + 1)).slice(-2); // Adding 1 to month as it's 0-indexed
    //     const day = ('0' + date.getDate()).slice(-2);
    //     return `${year}-${month}-${day}`;
    // }

    formatDate(date: Date): string {
        if (!date) {
          return '';
        }
        const year = date.getFullYear().toString(); // Keeping the full year
        const month = ('0' + (date.getMonth() + 1)).slice(-2); // Adding 1 to month as it's 0-indexed
        const day = ('0' + date.getDate()).slice(-2);
        return `${month}-${day}-${year}`; // Format mm-dd-yyyy
      }

    clear(table: Table) {
        table.clear();
        this.searchQuery = '';

        this.getAttendanceReport(
            {
                first: 0, rows: this.rows, sortField: '', sortOrder: 1
            }
        );

        this.dt.reset();
        this.showElements = 'true';
        this.company_name = '';
        this.location_name = '';
    }

    private AttendanceMonthlyMetricSubscription: Subscription;

    getAttendanceMonthlyMetrics() {
        this.AttendanceMonthlyMetricSubscription = interval(10000).pipe(
            startWith(0), // emit 0 immediately
            // Use switchMap to switch to a new observable (HTTP request) each time the interval emits
            switchMap(() => this.service.getAttendanceMonthlyMetrics()),
            // Use distinctUntilChanged to filter out repeated values
            distinctUntilChanged((prev, curr) => JSON.stringify(prev) === JSON.stringify(curr))
        ).subscribe((data: any) => {
            // this.metrics = data.daily_metrics;
            this.metricsDate = data.daily_metrics.map((item: any) => item.date);
            this.metricsPresent = data.daily_metrics.map((item: any) => item.present);
            this.metricsAbsent = data.daily_metrics.map((item: any) => item.absent);
            this.metricsLateEntry = data.daily_metrics.map((item: any) => item.late_entry);
            this.metricsEarlyExit = data.daily_metrics.map((item: any) => item.early_exit);
            this.metricsOvertime = data.daily_metrics.map((item: any) => item.overtime);

            this.initCharts();
        });
    }

    getCompaniesList() {

        const params: any = {
            page: 1,
            page_size: 100,
            sortField: '',
            ordering: '',
        };

        this.service.getCompanies(params).subscribe((data: any) => {
            this.companies = data.results;
        });
    }

    getLocationsList() {

        const params: any = {
            page: 1,
            page_size: 100,
            sortField: '',
            ordering: '',
        };

        this.service.getLocations(params).subscribe((data: any) => {
            this.locations = data.results;
        });
    }

    assignCompanyId(selectedCompany: any) {
        // Set the search query to the selected company ID
        this.company_name = selectedCompany.name;
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignLocationId(selectedLocation: any) {
        // Set the search query to the selected company ID
        this.location_name = selectedLocation.name;
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignDepartmentId(selectedDepartments: Department[]) {
        // Set the search query to the selected company ID
        this.department_names = selectedDepartments.map(department => department.name);
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignDesignationId(selectedDesignations: Designation[]) {
        // Set the search query to the selected company ID
        this.designation_names = selectedDesignations.map(designation => designation.name);
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    getEmployeeList() {

        this.service.getEmployeeDropdown().subscribe(data => {
            this.employeeList = data;
        });
    }

    assignEmployeeId(selectedEmployee: any) {
        this.employee_id = selectedEmployee.employee_id;
    }


    openExportModal() {
        this.visible = true;
    }

    downloadEmployeeMonthlyReport() {
        const params: any = {
            employee_id: this.employee_id || '',
            month: this.selectedMonth || '',
            year: this.selectedYear || '',
        };

        this.service.downloadEmployeeMonthlyReport(params).subscribe((data: any) => {
            const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'Employee_Monthly_Report.xlsx';
            link.click();
            window.URL.revokeObjectURL(url);
        });
    }

    onMonthSelect(event: any) {
        // Check if 'this.month' is a Date object
        if (this.month instanceof Date && !isNaN(this.month.getTime())) {
            // Convert year and month to numbers
            const year: number = this.month.getFullYear();
            const month: number = this.month.getMonth() + 1; // Months are 0-indexed, so add 1

            this.selectedYear = year;
            this.selectedMonth = month;

        } else {
            console.error("Invalid Date object:", this.month);
        }
    }

    downloadAllEmployeeMonthlyReport(params: any, actionType: string) {
        this.visible = true;
        this.counter = 0;
        this.startCounter();

        // Use 'allemployees' as the default actionType if report_status is empty
        const resolvedActionType = actionType || 'allemployees';

        this.service.downloadAllEmployeeMonthlyReport(params, resolvedActionType).subscribe({
            next: (data: any) => {
                // Create a Blob object from the response data
                const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

                // Create a URL for the Blob
                const url = window.URL.createObjectURL(blob);

                // Create a link element and set up the download
                const link = document.createElement('a');
                link.href = url;

                // Dynamically set the file name based on the resolved actionType and current date
                const reportFileName = this.getReportFileName(resolvedActionType);
                const currentDate = this.formatCurrentDate();
                link.download = `${reportFileName}_${currentDate}.xlsx`;

                // Append the link to the body, trigger the click, and remove the link
                document.body.appendChild(link);
                link.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(link);

                // Set visibility to false and show success message
                this.visible = false;
                this.stopCounter();
                this.messageService.add({
                    severity: 'success',
                    summary: 'Report Downloaded',
                    detail: 'The report is ready and has been downloaded successfully.'
                });
            },
            error: (error: any) => {
                // Handle any error that might occur during the download
                console.error('Error downloading the report:', error);

                // Set visibility to false and show error message
                this.stopCounter();
                this.visible = false;
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'An error occurred while downloading the report. Please try again.'
                });
            }
        });
    }


    // Helper function to format the current date as YYYY-MM-DD
    formatCurrentDate(): string {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
        const day = String(today.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    getReportFileName(actionType: string): string {
        const reportNames: { [key: string]: string } = {
            allemployees: 'Monthly_In_Out_Movements_Register',
            monthly_movements: 'Monthly_Movements_Register',
            monthly_duty_hours: 'Monthly_Duty_Hours_Register',
            monthly_muster_role: 'Monthly_Musterrole_Register',
            monthly_payroll: 'Monthly_Payroll_Register',
            monthly_shift_roaster: 'Monthly_Shift_Roaster_Register',
            monthly_overtime: 'Monthly_Overtime_Register',
            monthly_overtime_roundoff: 'Monthly_Overtime_Roundoff_Register',
            monthly_late_entry: 'Monthly_Late_Entry_Register',
            monthly_early_exit: 'Monthly_Early_Exit_Register',
            monthly_absent: 'Monthly_Absent_Register',
            monthly_present: 'Monthly_Present_Register',
        };
        return reportNames[actionType] || 'All_Employee_Monthly_Report';
    }

    onExportClick() {
        const params = {
            month: this.selectedMonth || '',
            year: this.selectedYear || '',
        };

        // Default to 'allemployees' if report_status is empty
        const actionType = this.report_status || 'allemployees';

        // Trigger the download with the selected parameters and actionType
        this.downloadAllEmployeeMonthlyReport(params, actionType);
    }

    counter: number = 0;
    private intervalId: any;

    startCounter() {
        this.intervalId = setInterval(() => {
            this.counter += 0.1; // Increment counter by 10ms in seconds
        }, 100); // Run every 10ms
    }

    stopCounter() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            this.counter = 0;
        }
        this.counter = 0;
    }

    ngOnDestroy() {

        if (this.AttendanceMonthlyMetricSubscription) {
            this.AttendanceMonthlyMetricSubscription.unsubscribe();
        }
    }

    customers: any[] = [
        {
            id: 1000,
            representative: {
                name: 'esrgesr rgerg',
                image: 'ionibowcher.png'
            },
            day_1: {
                time_in: '09:00',
                time_out: '17:00'
            },
            day_2: {
                time_in: '09:00',
                time_out: '17:00'
            },
            day_3: {
                time_in: '09:00',
                time_out: '17:00'
            },
            day_4: {
                time_in: '09:00',
                time_out: '17:00'
            },
            day_5: {
                time_in: '09:00',
                time_out: '17:00'
            }
        },
        // Add more customer objects as needed
    ];

    customers2: any[] = [
        {
            id: 1000,
            representative: {
                name: 'esrgesr rgerg',
                image: 'ionibowcher.png'
            },
            company: 'Company A',
            department: 'Department A',
            designation: 'Designation A',
            location: 'Location A',
            total_time: '40:00:00', // Total time for the employee
            days: [
                { day: 'Day 1', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 2', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 3', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 4', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 5', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 6', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 7', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 8', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 9', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 10', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 11', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 12', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 13', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 14', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 15', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 16', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 17', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 18', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 19', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 20', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 21', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 22', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 23', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 24', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 25', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 26', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 27', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 28', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 29', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 30', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' }
            ]
        },
        {
            id: 1001,
            representative: {
                name: 'asd asd',
                image: 'amyelsner.png'
            },
            company: 'Company B',
            department: 'Department A',
            designation: 'Designation A',
            location: 'Location A',
            total_time: '40:00:00', // Total time for the employee
            days: [
                { day: 'Day 1', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 2', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 3', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 4', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' },
                { day: 'Day 5', time_in: '09:00', time_out: '17:00', duration: '8:00:00', shift: 'FS' }
            ]
        },
    ];

    calculateTotalTime(representativeName: string): string {
        const employee = this.customers.find(c => c.representative.name === representativeName);
        if (employee) {
            const totalHours = employee.days.reduce((sum, day) => sum + parseInt(day.duration), 0);
            return `${totalHours} hours`;
        }
        return '0 hours';
    }

    calculateCustomerTotal(name: string) {
        let total = 0;

        if (this.customers) {
            for (let customer of this.customers) {
                if (customer.representative?.name === name) {
                    total++;
                }
            }
        }

        return total;
    }

    getSeverity(status: string) {
        switch (status) {
            case 'unqualified':
                return 'danger';

            case 'qualified':
                return 'success';

            case 'new':
                return 'info';

            case 'negotiation':
                return 'warning';

            case 'renewal':
                return null;

            default:
                return '';
        }
    }

}
