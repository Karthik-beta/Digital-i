import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { SharedService } from 'src/app/shared.service';
import { Table } from 'primeng/table';
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
  selector: 'app-missed-punch-report',
  templateUrl: './missed-punch-report.component.html',
  styleUrl: './missed-punch-report.component.scss'
})
export class MissedPunchReportComponent implements OnInit, OnDestroy {

    @ViewChild('dt') dt: Table;

    reportList: any

    pieData: any;

    pieOptions: any;

    barData: any;

    barOptions: any;

    combinedLogs: any[] = []; // Initialize as an array
    totalRecords: number = 0;
    rowsPerPageOptions: number[] = [10, 20, 30];
    rows: number = 10;
    currentPage: number = 1;
    loading: boolean = false;
    searchQuery: string = '';

    date: Date;

    rangeDates: Date[];

    shift_status: string = '';

    late_entry: boolean = false;

    early_exit: boolean = false;

    overtime: boolean = false;

    missed_punch: boolean = false;

    insufficient_duty_hours: boolean = false;

    company_name: string = '';

    location_name: string = '';

    department_name: string = '';

    designation_name: string = '';

    text: string = '';
    results: any[] = [];

    visible: boolean = false;

    position: string = 'top';

    presentCount: number=0;

    absentCount: number=0;

    lateEntryCount: number=0;

    earlyExitCount: number=0;

    overTimeCount: number=0;

    liveHeadCount: number=0;

    totalCheckIn: number=0;

    totalCheckOut: number=0;

    employeeList: any[] = [];

    companies: any[] = [];

    locations: any[] = [];

    departments: any[] = [];

    designations: any[] = [];

    selectedCompany: any;

    selectedLocation: any;

    selectedDepartment: any;

    selectedDesignation: any;

    employee_ids: string[] = [];

    location_names: string[] = [];

    company_names: string[] = [];

    department_names: string[] = [];

    designation_names: string[] = [];

    selectedLocations: Location[] = [];

    selectedCompanies: Company[] = [];

    selectedEmplyees: Employee[] = [];

    selectedDepartments: Department[] = [];

    selectedDesignations: Designation[] = [];

    stateOptions: any[] = [
        { label: 'Show', value: 'true' },
        { label: 'Hide', value: 'false' }
    ];

    showElements: string = 'true';

    items: MenuItem[] = [];

    criteria: Criteria[] | undefined;

    constructor(
        private service: SharedService,
        private messageService: MessageService,
    ) { }


    ngOnInit() {
        this.initCharts();

        this.items = [
            { label: 'PDF', icon: 'fas fa-download' },
            { label: 'Excel', icon: 'fas fa-download', command: () => this.downloadAttendanceReport() },
            // { separator: true },
        ];

        this.criteria = [
            { name: 'Present', code: 'P',command: () => this.searchAttendance('P') },
            { name: 'Absent', code: 'A', command: () => this.searchAttendance('A') },
            { name: 'Late Entry', code: 'LE', command: () => this.performAttendanceAction('lateEntry') },
            { name: 'Early Exit', code: 'EE', command: () => this.performAttendanceAction('earlyExit') },
            { name: 'Overtime', code: 'OT', command: () => this.performAttendanceAction('overtime') },
            { name: 'Missed Punch', code: 'MP', command: () => this.performAttendanceAction('missedPunch')},
            { name: 'Insufficient Duty Hours', code: 'IDH', command: () => this.performAttendanceAction('insufficientDutyHours')},
        ];

        this.getAttendanceMetrics();
        this.getEmployeeList();
        this.getCompaniesList();
        this.getLocationsList();
        this.getDepartmentsList();
        this.getDesignationList();
    }

    initCharts() {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
        const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

        this.pieData = {
            labels: ['Present', 'Absent', 'Late Entry', 'Early Exit', 'Overtime'],
            datasets: [
                {
                    data: [54, 32, 70, 43, 22],
                    backgroundColor: [
                        documentStyle.getPropertyValue('--green-500'),
                        documentStyle.getPropertyValue('--red-500'),
                        documentStyle.getPropertyValue('--indigo-500'),
                        documentStyle.getPropertyValue('--teal-500'),
                        documentStyle.getPropertyValue('--purple-500'),
                    ],
                    hoverBackgroundColor: [
                        documentStyle.getPropertyValue('--green-500'),
                        documentStyle.getPropertyValue('--red-500'),
                        documentStyle.getPropertyValue('--indigo-400'),
                        documentStyle.getPropertyValue('--teal-400'),
                        documentStyle.getPropertyValue('--purple-400'),
                    ]
                }]
        };

        this.pieOptions = {
            maintainAspectRatio: false,
            aspectRatio: 1.3,
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: false,
                        color: textColor
                    }
                }
            }
        };

        this.barData = {
            labels: [''],
            datasets: [
                {
                    label: 'Present',
                    backgroundColor: documentStyle.getPropertyValue('--green-400'),
                    borderColor: documentStyle.getPropertyValue('--green-400'),
                    data: [this.presentCount]
                },
                {
                    label: 'Absent',
                    backgroundColor: documentStyle.getPropertyValue('--red-400'),
                    borderColor: documentStyle.getPropertyValue('--red-400'),
                    data: [this.absentCount]
                },
                {
                    label: 'Late Entry',
                    backgroundColor: documentStyle.getPropertyValue('--indigo-400'),
                    borderColor: documentStyle.getPropertyValue('--indigo-400'),
                    data: [this.lateEntryCount]
                },
                {
                    label: 'Early Exit',
                    backgroundColor: documentStyle.getPropertyValue('--teal-400'),
                    borderColor: documentStyle.getPropertyValue('--teal-400'),
                    data: [this.earlyExitCount]
                },
                {
                    label: 'Overtime',
                    backgroundColor: documentStyle.getPropertyValue('--purple-400'),
                    borderColor: documentStyle.getPropertyValue('--purple-400'),
                    data: [this.overTimeCount]
                }
            ]
        };

        this.barOptions = {
            maintainAspectRatio: false,
            aspectRatio: 3,
            plugins: {
                legend: {
                    display: false,
                    labels: {
                        usePointStyle: true,
                        fontColor: textColor
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: textColorSecondary,
                        font: {
                            weight: 500
                        }
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                },
                y: {
                    ticks: {
                        color: textColorSecondary
                    },
                    grid: {
                        color: surfaceBorder,
                        drawBorder: false
                    }
                },
            }
        };
    }

    private AttendanceListSubscription: Subscription;

    getAttendanceReport(event: LazyLoadEvent) {
        this.loading = true;

        const params: any = {
            page: ((event.first || 0 ) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: event.sortField || '',
            ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
            search: this.searchQuery || '',
            logdate: this.date || '',
            shift_status: '',
            late_entry: false,
            early_exit: false,
            overtime: false,
            missed_punch: true,
            insufficient_duty_hours: false,
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

        console.log('Params:', params); // Check the params object

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

    onFilter(event: any) {
        console.log('Filter event:', event.filters); // Check the filter object

        const params: any = {
          // ... your other params
          employee_id_id: event.filters['employee_id_id'] ? event.filters['employee_id_id'][0].value : null
        };

        console.log('Updated params:', params); // Verify updated params
        this.getAttendanceReport(params);
    }

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    onDateChange(query: Date): void {
        const formattedDate = this.formatDate(query);
        this.searchQuery = formattedDate;
        this.dt.filterGlobal(formattedDate, 'contains');
        console.log(formattedDate);
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

    onCriteriaChange(event: any) {
        const selectedCriteria = event.value;
        if (selectedCriteria && selectedCriteria.command) {
            selectedCriteria.command();
        }
    }

    searchAttendance(criteria: string): void {
        // Set the searchQuery to the criteria you want to search, in this case 'P'
        this.shift_status = "A";

        // Reset all flags to false initially
        this.late_entry = false;
        this.early_exit = false;
        this.overtime = false;
        this.missed_punch = false;
        this.insufficient_duty_hours = false;

        // Perform the search
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });

        console.log('Search criteria:', criteria);
    }

    performAttendanceAction(actionType: string) {
        // Reset all flags to false
        this.shift_status = '';
        this.late_entry = false;
        this.early_exit = false;
        this.overtime = false;
        this.missed_punch = false;
        this.insufficient_duty_hours = false;

        switch(actionType) {
            case 'lateEntry':
                this.late_entry = true;
                break;
            case 'earlyExit':
                this.early_exit = true;
                break;
            case 'overtime':
                this.overtime = true;
                break;
            case 'missedPunch':
                this.missed_punch = true;
                break;
            case 'insufficientDutyHours':
                this.insufficient_duty_hours = true;
                break;
            default:
                // Handle default case if needed
                break;
        }
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    clear(table: Table) {
        table.clear();
        this.searchQuery = '';
        this.company_name = '';
        this.location_name = '';
        this.department_name = '';
        this.designation_name = '';
        this.date = null;
        this.rangeDates = null;
        this.shift_status = '';
        this.late_entry = false;
        this.early_exit = false;
        this.overtime = false;
        this.missed_punch = true;
        this.insufficient_duty_hours = false;
        this.employee_ids = [];
        this.company_names = [];
        this.location_names = [];
        this.department_names = [];
        this.designation_names = [];
        this.selectedEmplyees = [];
        this.selectedCompanies = [];
        this.selectedLocations = [];
        this.selectedDepartments = [];
        this.selectedDesignations = [];

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


    downloadAttendanceReport() {
        this.visible = true;

        const params: any = {
            employee_id: this.searchQuery || '',
            shift_status: this.shift_status || '',
            company_name: this.company_names.join(','),
            location_name: this.location_names.join(','),
            department_name: this.department_names.join(','),
            designation_name: this.designation_names.join(','),

            late_entry: this.late_entry || false,
            early_exit: this.early_exit || false,
            overtime: this.overtime || false,
            missed_punch: this.missed_punch || false,
        };

        if (this.rangeDates && this.rangeDates.length === 2 && this.rangeDates[0] && this.rangeDates[1]) {
            params.date_from = this.formatDate(this.rangeDates[0]);
            params.date_to = this.formatDate(this.rangeDates[1]);
        }

        this.service.downloadAttendanceReport(params).subscribe({
            next: (data) => {
                // Show dialog or perform any pre-download actions

                // Create a Blob object from the response data
                const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

                // Create a URL for the Blob
                const url = window.URL.createObjectURL(blob);

                // Create a link element and set up the download
                const a = document.createElement('a');
                a.href = url;

                // Get the current date and format it
                const currentDate = new Date();
                const formattedDate = currentDate.toISOString().split('T')[0];

                // Define the filename
                const filename = `Attendance_Report_${formattedDate}.xlsx`;
                a.download = filename;

                // Append the link to the body, trigger the click, and remove the link
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                // Set visibility to false and show success message
                this.visible = false;
                this.messageService.add({
                    severity: 'success',
                    summary: 'Report Downloaded',
                    detail: 'Report is ready to download'
                });
            },
            error: (error) => {
                // Handle any error that might occur during the download
                console.error('Error downloading attendance report:', error);

                // Set visibility to false and show error message
                this.visible = false;
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Error downloading the report'
                });
            }
        });
    }


    private AttendanceMetricSubscription: Subscription;

    getAttendanceMetrics() {
        this.AttendanceMetricSubscription = interval(10000).pipe(
            startWith(0), // emit 0 immediately
            // Use switchMap to switch to a new observable (HTTP request) each time the interval emits
            switchMap(() => this.service.getAttendanceMetrics()),
            // Use distinctUntilChanged to filter out repeated values
            distinctUntilChanged((prev, curr) => JSON.stringify(prev) === JSON.stringify(curr))
        ).subscribe((data: any) => {
            this.presentCount = data.present_count;
            this.absentCount = data.absent_count;
            this.lateEntryCount = data.late_entry_count;
            this.earlyExitCount = data.early_exit_count;
            this.overTimeCount = data.overtime_count;
            this.liveHeadCount = data.live_headcount;
            this.totalCheckIn = data.total_checkin;
            this.totalCheckOut = data.total_checkout;

            this.initCharts();
        });
    }

    getEmployeeList() {

        this.service.getEmployeeDropdown().subscribe(data => {
            this.employeeList = data;
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

    getDepartmentsList() {

        const params: any = {
            page: 1,
            page_size: 100,
            sortField: '',
            ordering: '',
        };

        this.service.getDepartments(params).subscribe((data: any) => {
            this.departments = data.results;
        }
        );
    }

    getDesignationList() {
        const params: any = {
            page: 1,
            page_size: 100,
            sortField: '',
            ordering: '',
        };

        this.service.getDesignations(params).subscribe((data: any) => {
            this.designations = data.results;
        });
    }

    assignEmployeeId(selectedEmployees: Employee[]) {
        // Set the search query to the selected employee ID
        this.employee_ids = selectedEmployees.map(employee => employee.employee_id);
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignCompanyId(selectedCompanies: Company[]) {
        // Set the search query to the selected company ID
        this.company_names = selectedCompanies.map(company => company.name);
        this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    // assignLocationId(selectedLocation: any) {
    //     // Set the search query to the selected company ID
    //     this.location_name = selectedLocation.name;
    //     this.getAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    // }
    assignLocationId(selectedLocations: Location[]) {
        // Set the search query to the selected company ID
        this.location_names = selectedLocations.map(location => location.name);
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

    ngOnDestroy() {
        if (this.AttendanceListSubscription) {
            this.AttendanceListSubscription.unsubscribe();
        }

        if (this.AttendanceMetricSubscription) {
            this.AttendanceMetricSubscription.unsubscribe();
        }
    }

}
