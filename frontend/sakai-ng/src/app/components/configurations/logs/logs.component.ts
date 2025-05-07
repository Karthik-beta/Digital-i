import { Component, OnInit, ViewChild } from '@angular/core';
import { Table } from 'primeng/table';
import { MenuItem } from 'primeng/api';
import { SharedService } from 'src/app/shared.service';
import { LazyLoadEvent } from 'primeng/api';
import { MessageService } from 'primeng/api';

interface Employee {
    employee_id: string;
}

@Component({
  selector: 'app-logs',
  templateUrl: './logs.component.html',
  styleUrl: './logs.component.scss'
})
export class LogsComponent implements OnInit {

    @ViewChild('dt') dt: Table;

    logList: any

    items: MenuItem[] = [];

    showElements: string = 'false';

    constructor(private service: SharedService, private messageService: MessageService) {}

    ngOnInit() {
        this.getEmployeeList();

        this.items = [
            { label: 'PDF', icon: 'fas fa-download' },
            { label: 'Excel', icon: 'fas fa-download', command: () => this.downloadLogsReport() },
        ];
    }

    totalRecords: number = 0;
    rowsPerPageOptions: number[] = [10, 20, 30];
    rows: number = 10;
    currentPage: number = 1;
    loading: boolean = false;
    searchQuery: string = '';
    visible: boolean = false;
    position: string = 'top';

    employeeList: any[] = [];

    employee_ids: string[] = [];

    selectedEmployees: Employee[] = [];

    rangeDates: Date[];

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'exact');
    }

    getLogReport(event: LazyLoadEvent): void {
        this.loading = true;

        const params: any = {
            page: ((event.first || 0 ) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: event.sortField || 'log_datetime',
            ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '-log_datetime',
            employee_ids: this.employee_ids.join(','),

        };

        if (this.rangeDates && this.rangeDates.length === 2 && this.rangeDates[0] && this.rangeDates[1]) {
            params.date_from = this.formatDate(this.rangeDates[0]);
            params.date_to = this.formatDate(this.rangeDates[1]);
        }

        // Include employeeid in the params if it exists
        if (this.searchQuery) {
            params.employeeid = this.searchQuery;  // Set employeeid directly
        }

        this.service.getLogReport(params).subscribe((data: any) => {
            this.logList = data.results;
            this.totalRecords = data.count;
            this.loading = false;
        });


    }

    getEmployeeList() {

        this.service.getEmployeeDropdown().subscribe(data => {
            this.employeeList = data;
        });
    }

    clear(table: Table) {
        table.clear();
        // this.showElements = 'false';
        this.dt.reset();
        this.rangeDates = null;
        this.searchQuery = '';
        this.employee_ids = [];
        this.selectedEmployees = [];
        this.assignEmployeeId(this.selectedEmployees);
        this.getLogReport({ first: 0, rows: this.rows, sortField: '', sortOrder: 1 });
    }

    assignEmployeeId(selectedEmployees: Employee[]) {
        this.employee_ids = selectedEmployees.map(employee => employee.employee_id);
        this.getLogReport({
            first: 0,
            rows: this.rows,
            sortField: '',
            sortOrder: 1
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
          this.getLogReport(params);
        }
    }

    formatDate(date: Date): string {
        if (!date) {
          return '';
        }
        const year = date.getFullYear().toString(); // Keeping the full year
        const month = ('0' + (date.getMonth() + 1)).slice(-2); // Adding 1 to month as it's 0-indexed
        const day = ('0' + date.getDate()).slice(-2);
        return `${year}-${month}-${day}`; // Format yyyy-mm-dd
    }

    downloadLogsReport() {
        this.visible = true;

        this.service.downloadLogsReport().subscribe({
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
                const filename = `Logs_Report_${formattedDate}.xlsx`;
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



}
