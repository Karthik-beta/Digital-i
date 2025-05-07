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
  selector: 'app-fixed-shift',
  templateUrl: './fixed-shift.component.html',
  styleUrl: './fixed-shift.component.scss'
})
export class FixedShiftComponent implements OnInit, OnDestroy {

    @ViewChild('dt') dt: Table;

    shifts: any[] = [];

    display: boolean = false;
    ModalTitle:string="";
    location: any;

    id: number = 0;
    name: string = '';
    shift_id: string = '';
    start_time: Date = new Date();
    end_time: Date = new Date();
    overtime_threshold: string;

    tolerance_start_time: Number | undefined;
    tolerance_end_time: Number | undefined;
    grace_start_time: Number | undefined;
    grace_end_time: Number | undefined;
    overtime_threshold_before_start: Number | undefined;
    overtime_threshold_after_end: Number | undefined;
    absent_threshold: Number | undefined;
    half_day_threshold: Number | undefined;
    full_day_threshold: Number | undefined;
    lunch_in_time: Date = new Date();
    lunch_out_time: Date = new Date();

    is_night_shift: boolean = false;
    consider_lunch_half_day: boolean = false;
    consider_lunch_full_day: boolean = false;

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

    private ShiftListSubscription: Subscription;

    getShiftsList(event: LazyLoadEvent): void {
        this.loading = true;

        const params: any = {
          page: ((event.first || 0) / (event.rows || 5) + 1).toString(),
          page_size: (event.rows || 10).toString(),
          sortField: event.sortField || '',
          ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
          search: this.searchQuery || '',

          // Add any other query parameters here
        };

        this.ShiftListSubscription = this.service.getShifts(params).subscribe({
            next: (response) => {
                this.shifts = response.results;
                this.totalRecords = response.count;
            },
            error: (error) => {
                // Handle error if needed
                console.error('Error fetching Shifts:', error);
            }
        });

        this.loading = false;
    }

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    clear(table: Table) {
        table.clear();
    }

    convertTo24HourFormat(date: Date): string {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = '00';
        return `${hours}:${minutes}:${seconds}`;
    }


    addClick() {
        this.id = null;
        this.name = '';
        this.shift_id = '';
        this.start_time = null;
        this.end_time = null;
        this.grace_start_time = null;
        this.grace_end_time = null;
        this.overtime_threshold_before_start = null;
        this.overtime_threshold_after_end = null;
        this.absent_threshold = null;
        this.half_day_threshold = null;
        this.full_day_threshold = null;
        this.lunch_in_time = null;
        this.lunch_out_time = null;
        this.is_night_shift = false;
        this.consider_lunch_half_day = false;
        this.consider_lunch_full_day = false;

        this.display = true;
        this.ModalTitle = "Add New Shift";
    }

    addShift() {
        // Convert start_time and end_time to 24-hour format if they are Date objects
        const formattedStartTime = this.convertTo24HourFormat(this.start_time);
        const formattedEndTime = this.convertTo24HourFormat(this.end_time);
        const formattedLunchInTime = this.convertTo24HourFormat(this.lunch_in_time || new Date('1970-01-01T00:00:00'));
        const formattedLunchOutTime = this.convertTo24HourFormat(this.lunch_out_time || new Date('1970-01-01T00:00:00'));

        const shift = {
            name: this.name,
            shift_id: this.shift_id,
            start_time: formattedStartTime,
            end_time: formattedEndTime,
            grace_period_at_start_time: this.grace_start_time || 0,
            grace_period_at_end_time: this.grace_end_time || 0,
            overtime_threshold_before_start: this.overtime_threshold_before_start || 0,
            overtime_threshold_after_end: this.overtime_threshold_after_end || 0,
            absent_threshold: this.absent_threshold || 0,
            half_day_threshold: this.half_day_threshold || 0,
            full_day_threshold: this.full_day_threshold || 0,
            lunch_in_time: formattedLunchInTime,
            lunch_out_time: formattedLunchOutTime,
            night_shift: this.is_night_shift,
            include_lunch_break_in_half_day: this.consider_lunch_half_day,
            include_lunch_break_in_full_day: this.consider_lunch_full_day
        }

        console.log(shift);
        this.loading = true;

        this.service.addShift(shift).subscribe({
            next: (response) => {
                this.dt.reset();

                this.eventEmitterService.invokeGetUpdatedAtList.emit();
                this.display = false;

                // Show success message
                this.messageService.add({
                severity: 'success',
                summary: 'Success',
                detail: `Successfully Added ${this.name} Shift`
                });
            },
            error: (error) => {
                // Show error message
                this.messageService.add({ severity: 'warn', summary: 'Failed', detail: `Failed to Add ${this.name} Shift` });
            }
        });

        this.getShiftsList({ first: 0, rows: 10, sortField: '', sortOrder: 1 });

        this.loading = false;
    }

    editClick(item: any) {

        this.id = item.id;
        this.name = item.name;
        this.shift_id = item.shift_id;
        this.start_time = new Date(`1970-01-01T${item.start_time}`);
        this.end_time = new Date(`1970-01-01T${item.end_time}`);
        this.grace_start_time = item.grace_period_at_start_time;
        this.grace_end_time = item.grace_period_at_end_time;
        this.overtime_threshold_before_start = item.overtime_threshold_before_start;
        this.overtime_threshold_after_end = item.overtime_threshold_after_end;
        this.absent_threshold = item.absent_threshold;
        this.half_day_threshold = item.half_day_threshold;
        this.full_day_threshold = item.full_day_threshold;
        this.lunch_in_time = item.lunch_in ? new Date(`1970-01-01T${item.lunch_in}`) : new Date('1970-01-01T00:00:00');
        this.lunch_out_time = item.lunch_out ? new Date(`1970-01-01T${item.lunch_out}`) : new Date('1970-01-01T00:00:00');
        this.is_night_shift = item.night_shift;
        this.consider_lunch_half_day = item.include_lunch_break_in_half_day;
        this.consider_lunch_full_day = item.include_lunch_break_in_full_day;

        this.display = true;
        this.ModalTitle = `Edit Shift ${item.name} Details`;
    }

    updateShift() {
        // Convert start_time and end_time to 24-hour format if they are Date objects
        const formattedStartTime = this.convertTo24HourFormat(this.start_time);
        const formattedEndTime = this.convertTo24HourFormat(this.end_time);
        const formattedLunchInTime = this.convertTo24HourFormat(this.lunch_in_time || new Date('1970-01-01T00:00:00'));
        const formattedLunchOutTime = this.convertTo24HourFormat(this.lunch_out_time || new Date('1970-01-01T00:00:00'));

        const shift = {
            id: this.id,
            name: this.name,
            shift_id: this.shift_id,
            start_time: formattedStartTime,
            end_time: formattedEndTime,
            tolerance_start_time: this.tolerance_start_time || 0,
            tolerance_end_time: this.tolerance_end_time || 0,
            grace_period_at_start_time: this.grace_start_time || 0,
            grace_period_at_end_time: this.grace_end_time || 0,
            overtime_threshold_before_start: this.overtime_threshold_before_start || 0,
            overtime_threshold_after_end: this.overtime_threshold_after_end || 0,
            absent_threshold: this.absent_threshold || 0,
            half_day_threshold: this.half_day_threshold || 0,
            full_day_threshold: this.full_day_threshold || 0,
            lunch_in: formattedLunchInTime || '00:00:00',
            lunch_out: formattedLunchOutTime || '00:00:00',
            night_shift: this.is_night_shift,
            include_lunch_break_in_half_day: this.consider_lunch_half_day,
            include_lunch_break_in_full_day: this.consider_lunch_full_day
        }

        this.loading = true;
        console.log(shift);

        this.service.updateShift(shift).subscribe({
            next: (response) => {
                this.dt.reset();
                this.eventEmitterService.invokeGetUpdatedAtList.emit();
                this.display = false;

                // Show success message
                this.messageService.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Successfully Updated ${this.name} Shift Details`
                });
            },
            error: (error) => {
                // Show error message if the update fails
                this.messageService.add({ severity: 'warn', summary: 'Failed', detail: `Failed to Update ${this.name} Shift Details` });
            }
        });

        this.getShiftsList({ first: 0, rows: 10, sortField: '', sortOrder: 1 });

        this.loading = false;
    }

    deleteClick(item: { id: any }) {
        // Extract the employee_id from the log object
        const id = item.id;

        // Display the confirmation dialog before proceeding with deletion
        this.confirmationService.confirm({
            message: 'Are you sure that you want to delete this Shift?',
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
                this.loading = true;

                // Call the deleteEmployee method from the service
                this.service.deleteShift(id).subscribe({
                    next: (response) => {

                        this.dt.reset();
                        this.eventEmitterService.invokeGetUpdatedAtList.emit();

                        // Show success message
                        this.messageService.add({
                          severity: 'success',
                          summary: 'Success',
                          detail: 'Shift has been deleted successfully.'
                        });
                    },
                    error: (error) => {
                        // Handle error if needed
                        console.error('Error deleting Shift:', error);

                        // Show error message
                        this.messageService.add({
                        severity: 'error',
                        summary: 'Error',
                        detail: 'Failed to delete Shift.'
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

        // Unsubscribe from the interval observable
        if (this.ShiftListSubscription) {
            this.ShiftListSubscription.unsubscribe();
        }
    }
}
