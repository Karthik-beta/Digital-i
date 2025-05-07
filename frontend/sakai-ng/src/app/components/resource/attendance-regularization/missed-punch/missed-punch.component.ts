import { Component, OnInit, Renderer2, ElementRef, ViewChild } from '@angular/core';
import { SharedService } from 'src/app/shared.service';
import { Table } from 'primeng/table';
import { MessageService } from 'primeng/api';
import { LazyLoadEvent } from 'primeng/api';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { format } from 'path';
import { time } from 'console';

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
    @ViewChild('dt') dt: Table;

    totalRecords: number = 0;

    rowsPerPageOptions: number[] = [10, 20, 30];

    rows: number = 10;

    currentPage: number = 1;

    loading: boolean = false;

    logList: any[] = [];

    visible: boolean = false;

    employeeList: any[] = [];

    directionList: any[] = [];

    employee_id: string='';

    selectedEmployee: any;

    employeeDropdown: EmployeeDropdown[] = [];

    datetime: Date[] | undefined;

    month: Date = new Date();

    selectedMonth: any;

    selectedYear: any;

    DateTime: string = '';

    direction: string = '';

    searchQuery: string = '';

    List: any[] = [];

    logForm: FormGroup;

    formGroup = new FormGroup({
        employee: new FormControl(null),
        date: new FormControl(null),
    });


    showDialog() {
        this.visible = true;
    }

    constructor(private service: SharedService, private messageService: MessageService, private fb: FormBuilder, private renderer: Renderer2) { }

    ngOnInit(): void {
        this.getEmployeeDropdown();

        this.initForm();

        // this.getDatesArray();
        // this.getEmployeesArray();

        this.directionList = [
            { label: 'In Device', value: 'In Device' },
            { label: 'Out Device', value: 'Out Device' },
        ];
    }

    getAttendanceOverview(event: LazyLoadEvent ){
        this.loading = true;

        const params: any = {
            page: ((event.first || 0 ) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: event.sortField || '',
            ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
            month: this.selectedMonth || this.month.getMonth() + 1,
            year: this.selectedYear || this.month.getFullYear(),
            search: this.searchQuery || '',
        };

        console.log('Params', params);

        this.service.getMonthlyAttendanceOverview(params).subscribe(data => {
            this.List = data.results;
            this.totalRecords = data.count;
            this.loading = false;
            this.datesArray = data.results.dates;
            this.employeesArray = data.results.employees;
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

    formatdateTime(time: Date): string {
        if (!time) {
            return '';
        }
        const year = time.getFullYear().toString();
        const month = ('0' + (time.getMonth() + 1)).slice(-2);
        const day = ('0' + time.getDate()).slice(-2);
        const hours = ('0' + time.getHours()).slice(-2);
        const minutes = ('0' + time.getMinutes()).slice(-2);
        const timezoneOffset = -time.getTimezoneOffset();
        const timezoneHours = ('0' + Math.floor(Math.abs(timezoneOffset) / 60)).slice(-2);
        const timezoneMinutes = ('0' + (Math.abs(timezoneOffset) % 60)).slice(-2);
        const timezoneSign = timezoneOffset >= 0 ? '+' : '-';

        return `${year}-${month}-${day} ${hours}:${minutes}:00`;
    }

    // dateSelect() {
    //     console.log("Datetime", this.datetime);
    //     // const formattedDate = this.formatDate(this.dateValue);
    //     // console.log(formattedDate);
    // }

    employeeSelect(event: any) {
        this.selectedEmployee = event.value.employee_id;
    }

    dateTimeSelect(event: Date) {
        event.setSeconds(0); // Set seconds to 0

        const formattedDateTime = event.toLocaleString('sv-SE', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }).replace(',', ''); // Remove seconds if necessary

        this.DateTime = formattedDateTime
    }

    directionSelect(event: any) {
        this.direction = event.value.value;
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

        // You can access the form values like this:
        const employee = this.logForm.get('employee')?.value;
        const employeeId = employee.employee_id;

        const formattedDateTime = this.dateTimeSelect(this.logForm.get('date')?.value);

        const date = this.logForm.get('date')?.value;
        const formattedDate = this.formatDate(date);

        const time = this.logForm.get('time')?.value;
        const formattedTime = this.formatdateTime(time);

        const formData = {
            employeeid: this.selectedEmployee,
            log_datetime: this.DateTime,
            direction: this.direction,
        };

        this.service.postLog(formData).subscribe({
            next: (data) => {
                console.log('Log created successfully');
                this.visible = false;
                // this.getLogs({ first: 0, rows: this.rows });
                this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Log created successfully' });
            },
            error : (error) => {
                console.error('Error creating log', error);
                this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Error creating log' });
            }
        });

    }

    setDefaultMonth() {
        this.selectedYear = this.month.getFullYear();
        this.selectedMonth = this.month.getMonth() + 1; // Months are 0-indexed, so add 1
    }

    onMonthSelect(event: any) {
        if (this.month instanceof Date && !isNaN(this.month.getTime())) {
            // Convert year and month to numbers
            const year: number = this.month.getFullYear();
            const month: number = this.month.getMonth() + 1; // Months are 0-indexed, so add 1

            this.selectedYear = year;
            this.selectedMonth = month;

            this.getAttendanceOverview({});

        } else {
            console.error("Invalid Date object:", this.month);
        }
    }

    data: any = {
        dates: [],
        employees: []
    };

    datesArray: { date: string; day: string }[] = [];
    employeesArray: any[] = [];

    getDatesArray() {
        this.datesArray = this.List[0].dates; // Direct assignment, no looping needed
    }

    getEmployeesArray() {
        this.employeesArray = this.List[0].employees; // Direct assignment, no looping needed
    }

    getAttendance(employee: any, date: string): string {
        return employee.attendance[date] ? `<span class="block text-blue-500 font-bold cursor-pointer" ><i class="pi pi-pencil" style="color: slateblue" (onClick)="editItem()"></i></span><br /><span class="font-bold">In:</span>${employee.attendance[date].time_in} <br /> <span class="font-bold">Out:</span>${employee.attendance[date].time_out}` : '';
    }

    // getAttendance(employee: any, date: string): string {
    //     return employee.attendance[date]
    //         ? `<span class="block text-blue-500 font-bold cursor-pointer edit-icon" data-employee-id="${employee.employee_id}" data-date="${date}">
    //              <i class="pi pi-pencil" style="color: slateblue"></i>
    //            </span><br />
    //            <span class="font-bold">In:</span> ${employee.attendance[date].time_in} <br />
    //            <span class="font-bold">Out:</span> ${employee.attendance[date].time_out}`
    //         : '';
    // }

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    selectedDate: string = '';
    selectedDay: string = '';
    selectedId: number = 0;
    selectedTimeIn: Date | null = null;
    selectedTimeOut: Date | null = null;


    editItem(id:number, timeIn: string | null, timeOut: string | null, date: string, day:string, employee: any) {
        this.selectedId = id;
        this.selectedEmployee = employee;
        this.selectedDate = date;
        this.selectedDay = day;
        // this.selectedTimeIn = timeIn;
        // this.selectedTimeOut = timeOut;

        // Convert time strings to Date objects
        this.selectedTimeIn = timeIn ? this.parseDateTime(timeIn) : null;
        this.selectedTimeOut = timeOut ? this.parseDateTime(timeOut) : null;

        this.visible = true;

        console.log('Selected Employee', this.selectedTimeIn, this.selectedTimeOut);
    }

    // Helper function to convert "YYYY-MM-DD HH:mm" string to Date object
    parseDateTime(dateTimeStr: string): Date {
        const [datePart, timePart] = dateTimeStr.split(' ');
        const [year, month, day] = datePart.split('-').map(Number);
        const [hour, minute] = timePart.split(':').map(Number);

        return new Date(year, month - 1, day, hour, minute); // Month is 0-based in JS Dates
    }

    timeInChanged: boolean = false;
    timeOutChanged: boolean = false;

    onTimeInChange(event: any) {
        this.timeInChanged = true;
    }

    onTimeOutChange(event: any) {
        this.timeOutChanged = true;
    }

    updateItem(id: number) {
        const formData: any = { id: this.selectedId };

        if (this.timeInChanged) {
            formData.time_in = this.selectedTimeIn ? this.formatdateTime(this.selectedTimeIn) : null;
        }

        if (this.timeOutChanged) {
            formData.time_out = this.selectedTimeOut ? this.formatdateTime(this.selectedTimeOut) : null;
        }

        if (Object.keys(formData).length === 1) {
            // No fields to update
            this.messageService.add({ severity: 'info', summary: 'No Changes', detail: 'No changes detected' });
            return;
        }

        console.log('Form Data', formData);

        this.loading = true;

        this.service.updateMissedPunch(id, formData).subscribe({
            next: (response) => {
                this.getAttendanceOverview({});
                this.visible = false;

                this.getAttendanceOverview({
                    first: (this.currentPage - 1) * this.rows,
                    rows: this.rows,
                });

                this.messageService.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: 'Successfully Updated Attendance Details'
                });

                // Reset change tracking
                this.timeInChanged = false;
                this.timeOutChanged = false;
            },
            error: (error) => {
                this.messageService.add({ severity: 'warn', summary: 'Failed', detail: 'Failed to Update Attendance Details' });
            }
        });

        this.loading = false;
    }



    // List: any[] = [
    //     {
    //         dates: [
    //             { date: '01', day: 'Monday' },
    //             { date: '02', day: 'Tuesday' },
    //             { date: '03', day: 'Wednesday' },
    //         ],
    //         employees: [
    //             {
    //                 employee_id: '1',
    //                 employee_name: 'A',
    //                 attendance: {
    //                     '01': { id: 2, time_in: '08:00', time_out: '17:00' },
    //                     '02': { id: 5, time_in: '08:00', time_out: '17:00' },
    //                     '03': { id: 23, time_in: '08:00', time_out: '17:00' },
    //                 }
    //             },
    //             {
    //                 employee_id: '2',
    //                 employee_name: 'B',
    //                 attendance: {
    //                     '01': { id: 76, time_in: '09:00', time_out: '18:00' },
    //                     '02': { id: 56, time_in: '09:00', time_out: '18:00' },
    //                     '03': { id: 34, time_in: '09:00', time_out: '18:00' },
    //                 }
    //             },
    //             {
    //                 employee_id: '3',
    //                 employee_name: 'C',
    //                 attendance: {
    //                     '01': { id: 2, time_in: '07:00', time_out: '16:00' },
    //                     '02': { id: 2, time_in: '07:00', time_out: '16:00' },
    //                     '03': { id: 2, time_in: '07:00', time_out: '' },
    //                 }
    //             },
    //             {
    //                 employee_id: '4',
    //                 employee_name: 'D',
    //                 attendance: {
    //                     '01': { time_in: '10:00', time_out: '19:00' },
    //                     '02': { time_in: '10:00', time_out: '19:00' },
    //                     '03': { time_in: '10:00', time_out: '19:00' },
    //                     '04': { time_in: '10:00', time_out: '19:00' },
    //                     '05': { time_in: '10:00', time_out: '19:00' },
    //                     '06': { time_in: '10:00', time_out: '19:00' },
    //                     '07': { time_in: '10:00', time_out: '19:00' },
    //                     '08': { time_in: '10:00', time_out: '19:00' },
    //                 }
    //             }
    //         ]
    //     }
    // ];

}
