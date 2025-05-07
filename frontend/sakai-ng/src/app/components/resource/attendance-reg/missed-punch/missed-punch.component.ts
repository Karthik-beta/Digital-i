import { Component, OnInit } from '@angular/core';
import { SharedService } from 'src/app/shared.service';
import { Table } from 'primeng/table';
import { MessageService } from 'primeng/api';
import { LazyLoadEvent } from 'primeng/api';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

interface EmployeeDropdown {
    employee_id: string;
    employee_name: string;
}

@Component({
  selector: 'app-missed-punch',
  templateUrl: './missed-punch.component.html',
  styleUrl: './missed-punch.component.scss'
})
export class MissedPunchComponent implements OnInit {

    totalRecords: number = 0;

    rowsPerPageOptions: number[] = [10, 20, 30];

    rows: number = 10;

    currentPage: number = 1;

    loading: boolean = false;

    logList: any[] = [];

    visible: boolean = false;

    employeeList: any[] = [];

    employee_id: string='';

    selectedEmployee: any;

    employeeDropdown: EmployeeDropdown[] = [];

    dateValue: Date;

    logForm: FormGroup;

    showDialog() {
        this.visible = true;
    }

    constructor(private service: SharedService, private messageService: MessageService, private fb: FormBuilder) { }

    ngOnInit(): void {
        this.getEmployeeDropdown();

        this.initForm();
    }

    getLogs(event: LazyLoadEvent ){
        this.loading = true;

        const params: any = {
            page: ((event.first || 0 ) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: event.sortField || '',
            ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
        };

        this.service.getLogList(params).subscribe(data => {
            this.logList = data.results;
            this.totalRecords = data.count;
            this.loading = false;
        });
    }

    getEmployeeDropdown() {
        this.service.getEmployeeDropdown().subscribe(data => {
            this.employeeList = data;
        });
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

    formatTime(time: Date): string {
        if (!time) {
          return '';
        }
        const hours = ('0' + time.getHours()).slice(-2);
        const minutes = ('0' + time.getMinutes()).slice(-2);
        return `${hours}:${minutes}`;
    }

    dateSelect() {
        const formattedDate = this.formatDate(this.dateValue);
        console.log(formattedDate);
    }

    initForm() {
        this.logForm = this.fb.group({
            employee: ['', Validators.required],
            date: ['', Validators.required],
            time: ['', Validators.required],
        });
    }

    onSubmit() {
        // Handle form submission logic here
        console.log(this.logForm.value);

        // You can access the form values like this:
        const employee = this.logForm.get('employee')?.value;
        const employeeId = employee.employee_id;

        const date = this.logForm.get('date')?.value;
        const formattedDate = this.formatDate(date);

        const time = this.logForm.get('time')?.value;
        const formattedTime = this.formatTime(time);

        const formData = {
            idno: 1,
            employeeid: employeeId,
            logdate: formattedDate,
            logtime: formattedTime,
            direction: 'Manual',
            shortname: 'M',
            serialno: ''
        };

        this.service.postLog(formData).subscribe({
            next: (data) => {
                console.log('Log created successfully');
                this.visible = false;
                this.getLogs({ first: 0, rows: this.rows });
                this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Log created successfully' });
            },
            error : (error) => {
                console.error('Error creating log', error);
                this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Error creating log' });
            }
        });

    }

}
