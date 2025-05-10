import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { SharedService } from 'src/app/shared.service';
import { DataService } from 'src/app/service/dataservice/data.service';
import { Table } from 'primeng/table';
import { TableLazyLoadEvent } from 'primeng/table';
import { LazyLoadEvent } from 'primeng/api';
import { MessageService, ConfirmationService, ConfirmEventType } from 'primeng/api';
import { MenuItem } from 'primeng/api';
import { debounceTime, distinctUntilChanged, startWith, switchMap, timeout, catchError } from 'rxjs/operators';
import { Observable, Subscription, interval, timer } from 'rxjs';
import { of } from 'rxjs';

@Component({
  selector: 'app-employee-master',
  standalone: false,
//   imports: [],
  templateUrl: './employee-master.component.html',
  styleUrl: './employee-master.component.scss'
})
export class EmployeeMasterComponent implements OnInit, OnDestroy {

    @ViewChild('dt') dt: Table;

    totalRecords: number = 0;
    rowsPerPageOptions: number[] = [10, 20, 30, 50];
    rows: number = this.rowsPerPageOptions[0];
    currentPage: number = 1;
    loading: boolean = true;
    searchQuery: string = '';
    employees: any[] = [];
    employeeStats: any[] = [];


    text: string = '';
    results: any[] = [];

    items: MenuItem[] = [];

    constructor(
        private service: SharedService,
        private messageService: MessageService,
        private confirmationService: ConfirmationService,
        private dataService: DataService,
        private router: Router
    )
    {

    }




    ngOnInit(): void {

        this.getEmployeeStats();

        this.items = [
            { label: 'Import', icon: 'fas fa-file-import' },
            { label: 'Export', icon: 'fas fa-download' },
        ];

        // Load employees data from session storage if available
        const sessionEmployees = sessionStorage.getItem('employees');
        if (sessionEmployees) {
        this.employees = JSON.parse(sessionEmployees);
        }
    }

    totalOnboarded: number = 0;
    totalMale: number = 0;
    totalFemale: number = 0;
    totalOters: number = 0;
    total_new_employees_this_month: number = 0;
    total_new_employees_since_last_month: number = 0;
    total_resigned_this_month: number = 0;
    total_employees_resigned_since_last_month: number = 0;



    getEmployeeStats(): void {
        this.service.getEmployeeStats().pipe(
            timeout(60000), // Set timeout to 10 seconds
            catchError(error => {
                console.error('Error fetching employee stats:', error);
                this.loading = false;
                return of({ results: [], count: 0 }); // Return an empty result set in case of error
            })
        ).subscribe((data: any) => {
            this.employeeStats = data.results;
            this.totalOnboarded = data.total_employees;
            this.totalMale = data.total_male;
            this.totalFemale = data.total_female
            this.totalOters = data.total_others;
            this.total_new_employees_this_month = data.total_new_employees_this_month;
            this.total_new_employees_since_last_month = data.total_new_employees_since_last_month;
            this.total_resigned_this_month = data.total_resigned_this_month;
            this.total_employees_resigned_since_last_month = data.total_employees_resigned_since_last_month;
        });
    }

    private EmployeesListSubscription: Subscription;

    getEmployeesList(event: LazyLoadEvent): void {
        this.loading = true;

        const params: any = {
            page: ((event.first || 0 ) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: event.sortField || '',
            ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
            search: this.searchQuery || '',
        };

        // Use startWith to trigger an initial HTTP request
        this.EmployeesListSubscription = interval(100000).pipe(
            startWith(0), // emit 0 immediately
            // Use switchMap to switch to a new observable (HTTP request) each time the interval emits
            switchMap(() => this.service.getEmployeeList(params).pipe(
                timeout(10000), // Set timeout to 10 seconds
                catchError(error => {
                    console.error('Request timed out or failed', error);
                    this.loading = false;
                    return of({ results: [], count: 0 }); // Return an empty result set in case of error
                })
            )),
            // Use distinctUntilChanged to filter out repeated values
            distinctUntilChanged((prev, curr) => JSON.stringify(prev) === JSON.stringify(curr))
        ).subscribe((data: any) => {
            this.employees = data.results;
            this.totalRecords = data.count;
            this.loading = false;

            // Store employees data in session storage
            // sessionStorage.setItem('employees', JSON.stringify(this.employees));
        });
    }

    deleteEmployee(id: number): void {

        console.log('Deleting employee with id:', id);
        this.confirmationService.confirm({
            message: 'Are you sure you want to delete this employee?',
            header: 'Delete Employee',
            icon: 'pi pi-exclamation-triangle',
            acceptButtonStyleClass:"p-button-danger p-button-text",
            rejectButtonStyleClass:"p-button-text p-button-text",
            accept: () => {
                this.service.deleteEmployee(id).subscribe({
                    next: (response) => {
                        this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Employee deleted successfully' });
                        this.getEmployeesList({ first: 0, rows: this.rows });
                    },
                    error: (error) => {
                        this.messageService.add({ severity: 'warn', summary: 'Error', detail: 'Failed to delete employee' });
                    }
                });
            },
            reject: (type: any) => {
                switch (type) {
                    case ConfirmEventType.REJECT:
                        this.messageService.add({ severity: 'info', summary: 'Info', detail: 'Delete operation rejected' });
                        break;
                    case ConfirmEventType.CANCEL:
                        this.messageService.add({ severity: 'warn', summary: 'Warn', detail: 'Delete operation cancelled' });
                        break;
                }
            }
        });
    }


    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    clear(table: Table) {
        table.clear();
    }



    ngOnDestroy() {
        if (this.EmployeesListSubscription) {
            this.EmployeesListSubscription.unsubscribe();
        }
    }

}
