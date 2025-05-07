import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Table } from 'primeng/table';
import { LazyLoadEvent } from 'primeng/api';
import { SharedService } from 'src/app/shared.service';
import { EventemitterService } from 'src/app/service/eventemitter/eventemitter.service';
import { debounceTime, distinctUntilChanged, startWith, switchMap, tap } from 'rxjs/operators';
import { Observable, Subscription, interval, timer } from 'rxjs';
import { MessageService, ConfirmationService, ConfirmEventType } from 'primeng/api';

@Component({
  selector: 'app-department',
  standalone: false,
//   imports: [],
  templateUrl: './department.component.html',
  styleUrl: './department.component.scss'
})
export class DepartmentComponent implements OnInit, OnDestroy {

    @ViewChild('dt') dt: Table;

    departments: any[] = [];

    display: boolean = false;
    ModalTitle:string="";
    company: any;

    id: number = 0;
    name: string = '';
    code: string = '';

    constructor(
        private service:SharedService,
        private messageService: MessageService,
        private confirmationService: ConfirmationService,
        private eventEmitterService: EventemitterService
    ) {}

    ngOnInit() {

    }

    totalRecords: number = 0;
    rowsPerPageOptions: number[] = [5, 10, 20, 30];
    rows: number = this.rowsPerPageOptions[0];
    currentPage: number = 1;
    loading: boolean = true;
    searchQuery: string = '';

    private DepartmentsListSubscription: Subscription;

    getDepartmentsList(event: LazyLoadEvent): void {
        this.loading = true;

        const params: any = {
          page: ((event.first || 0) / (event.rows || 5) + 1).toString(),
          page_size: (event.rows || 10).toString(),
          sortField: event.sortField || '',
          ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
          search: this.searchQuery || '',
        };

        // Use startWith to trigger an initial HTTP request
        this.DepartmentsListSubscription = interval(10000).pipe(
            startWith(0), // emit 0 immediately
            // Use switchMap to switch to a new observable (HTTP request) each time the interval emits
            switchMap(() => this.service.getDepartments(params)),
            // Use distinctUntilChanged to filter out repeated values
            distinctUntilChanged((prev, curr) => JSON.stringify(prev) === JSON.stringify(curr))
            ).subscribe((data: any) => {
            this.departments = data.results;
            this.totalRecords = data.count;
            this.loading = false;
        });

        console.log('getLogReport', params);
    }

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    clear(table: Table) {
        table.clear();
    }

    addClick() {

        this.id = 0;
        this.name = '';
        this.code = '';

        this.display = true;
        this.ModalTitle = "Add New Department";
    }

    addDepartment(): void {
        const department = {
            name: this.name,
            code: this.code,
        };

        this.loading = true;

        this.service.addDepartment(department).subscribe({
            next: (response) => {
                this.dt.reset();

                this.eventEmitterService.invokeGetUpdatedAtList.emit();
                this.display = false;

                // Show success message
                this.messageService.add({
                severity: 'success',
                summary: 'Success',
                detail: 'Successfully Added New Department'
                });
            },
            error: (error) => {
                // Show error message
                this.messageService.add({ severity: 'warn', summary: 'Failed', detail: 'Failed to Add New Department' });
            }
        });

        this.loading = false;
    }



    editClick(item: any) {

        this.id = item.id;
        this.name = item.name;
        this.code = item.code;

        this.display = true;
        this.ModalTitle = "Edit Department";
    }

    updateDepartment(): void {
        const department = {
            id: this.id,
            name: this.name,
            code: this.code,
        };

        this.loading = true;

        this.service.updateDepartment(department).subscribe({
            next: (response) => {
                this.dt.reset();

                this.eventEmitterService.invokeGetUpdatedAtList.emit();
                this.display = false;

                // Show success message
                this.messageService.add({
                severity: 'success',
                summary: 'Success',
                detail: 'Successfully Updated Department Details'
                });
            },
            error: (error) => {
                // Show error message
                this.messageService.add({ severity: 'warn', summary: 'Failed', detail: 'Failed to Update Department Details' });
            }
        });

        this.loading = false;
    }



    deleteClick(item: { id: any }) {
        // Extract the employee_id from the log object
        const id = item.id;

        // Display the confirmation dialog before proceeding with deletion
        this.confirmationService.confirm({
            message: 'Are you sure that you want to delete this Department?',
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
                this.loading = true;

                // Call the deleteEmployee method from the service
                this.service.deleteDepartment(id).subscribe({
                    next: (response) => {

                        this.dt.reset();
                        this.eventEmitterService.invokeGetUpdatedAtList.emit();

                        // Show success message
                        this.messageService.add({
                          severity: 'success',
                          summary: 'Success',
                          detail: 'Department has been deleted successfully.'
                        });
                    },
                    error: (error) => {
                        // Handle error if needed
                        console.error('Error deleting Department:', error);

                        // Show error message
                        this.messageService.add({
                        severity: 'error',
                        summary: 'Error',
                        detail: 'Failed to delete department.'
                        });
                    }
                });

                this.loading = false;
            },
            reject: () => {
                // User rejected the confirmation, do nothing or handle as needed
                this.messageService.add({ severity: 'error', summary: 'Rejected', detail: 'You have Cancelled' });
                // console.log('Deletion cancelled by user.');
            }
        });
    }

    ngOnDestroy() {
        if (this.DepartmentsListSubscription) {
            this.DepartmentsListSubscription.unsubscribe();
        }
    }

}
