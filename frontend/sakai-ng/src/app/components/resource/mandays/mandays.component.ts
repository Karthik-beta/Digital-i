import { Component, OnInit, ViewChild } from '@angular/core';
import { SharedService } from 'src/app/shared.service';
import { MessageService } from 'primeng/api';
import { LazyLoadEvent } from 'primeng/api';
import { Table } from 'primeng/table';
import { MenuItem } from 'primeng/api';
import { Calendar } from 'primeng/calendar';

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

@Component({
  selector: 'app-mandays',
  templateUrl: './mandays.component.html',
  styleUrl: './mandays.component.scss'
})
export class MandaysComponent implements OnInit {

    @ViewChild('dt') dt: Table;
    @ViewChild('calendar') calendar!: Calendar;

    mandaysAttendanceList: any[] = [];
    totalRecords: number = 0;
    rowsPerPageOptions: number[] = [10, 20, 30];
    rows: number = 10;
    currentPage: number = 1;
    loading: boolean = false;
    showElements: string = 'true';
    visible: boolean = false;
    position: string = 'top';
    dateSelected: Date = new Date();
    dateSelectedString: string = '';
    logdate: string = '';

    searchQuery: string = '';

    items: MenuItem[] = [];

    date: Date;

    rangeDates: Date[];

    employeeList: any[] = [];

    companies: any[] = [];

    locations: any[] = [];

    departments: any[] = [];

    designations: any[] = [];

    employee_ids: string[] = [];

    location_names: string[] = [];

    company_names: string[] = [];

    department_names: string[] = [];

    designation_names: string[] = [];

    selectedLocations: Location[] = [];

    selectedCompanies: Company[] = [];

    selectedEmployees: Employee[] = [];

    selectedDepartments: Department[] = [];

    selectedDesignations: Designation[] = [];

    constructor(private service: SharedService, private messageService: MessageService,) { }

    ngOnInit(): void {

        this.items = [
            // { label: 'Import', icon: 'fas fa-file-import' },
            { label: 'Export Mandays Movements', icon: 'fas fa-download', command: () => this.downloadMandaysAttendanceReport() },
            { label: 'Export Mandays Worked', icon: 'fas fa-download', command: () => this.downloadMandaysWorkedReport() },
            { separator: true },
            { label: 'Reprocess Report', icon: 'fas fa-redo-alt', command: () => this.postReprocessLogs() },
        ];

        this.getEmployeeList();
        this.getCompaniesList();
        this.getLocationsList();
        this.getDepartmentsList();
        this.getDesignationList();
    }

    onDateChange(event: any) {
        if (event) {
            const selectedDate = new Date(event);
            this.dateSelected = selectedDate;
            this.dateSelectedString = this.formatDate(this.dateSelected);
        } else {
            this.dateSelected = null;
            this.dateSelectedString = '';
        }
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
        this.getMandaysAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignCompanyId(selectedCompanies: Company[]) {
        // Set the search query to the selected company ID
        this.company_names = selectedCompanies.map(company => company.name);
        this.getMandaysAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignLocationId(selectedLocations: Location[]) {
        // Set the search query to the selected company ID
        this.location_names = selectedLocations.map(location => location.name);
        this.getMandaysAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignDepartmentId(selectedDepartments: Department[]) {
        // Set the search query to the selected company ID
        this.department_names = selectedDepartments.map(department => department.name);
        this.getMandaysAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignDesignationId(selectedDesignations: Designation[]) {
        // Set the search query to the selected company ID
        this.designation_names = selectedDesignations.map(designation => designation.name);
        this.getMandaysAttendanceReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    formatDate(date: Date): string {
        if (!date) {
          return '';
        }
        const year = date.getFullYear().toString(); // Keeping the full year
        const month = ('0' + (date.getMonth() + 1)).slice(-2); // Adding 1 to month as it's 0-indexed
        const day = ('0' + date.getDate()).slice(-2);
        return `${month}-${day}-${year}`; // Format mm-dd-yyyy
    }

    downloadMandaysAttendanceReport() {
        this.visible = true;

        const params: any = {
            search: this.searchQuery || '',
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

        this.service.downloadMandaysAttendanceReport(params).subscribe({
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
                const filename = `Mandays_Report_${formattedDate}.xlsx`;
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

    clear(table: Table) {
        table.clear();
        // this.showElements = 'true';
        if (this.calendar) {
            this.calendar.value = null;
            this.calendar.updateInputfield();
        }
        this.dateSelected = null; // Reset the model value
        this.dateSelectedString = ''; // Clear the formatted string
        this.onDateChange(null);
    }

    downloadMandaysWorkedReport() {
        this.visible = true;

        const params: any = {
            search: this.searchQuery || '',
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

        this.service.downloadMandaysWorkedReport(params).subscribe({
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
                const filename = `Mandays_Report_${formattedDate}.xlsx`;
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

    postReprocessLogs() {
        this.service.reProcessLogs().subscribe({
            next: (data) => {
                // Show success message
                this.messageService.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: 'The report is being reprocessed. Please wait for up to 2 minutes to view/download the report.'
                });
            },
            error: (error) => {
                // Show error message
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to reprocess logs'
                });
            }
        });
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

        this.getMandaysAttendanceReport(params);
        }
    }

    downloadMandaysMissedPunchReport() {
        this.visible = true;

        const params: any = {
            date: this.dateSelectedString,
        };

        this.service.downloadMandaysMissedPunchReport(params).subscribe({
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
                const filename = `Mandays_Missed_Punch_${formattedDate}.xlsx`;
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


    getMandaysAttendanceReport(event: LazyLoadEvent) {
        this.loading = true;

        const params: any = {
            page: ((event.first || 0 ) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: event.sortField || '',
            ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
            search: this.searchQuery || '',
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

        this.service.getMandaysAttendanceList(params).subscribe((data: any) => {
            console.log(data);
            this.mandaysAttendanceList = data.results;
            this.totalRecords = data.count;
            this.loading = false;
        });
    }


}
