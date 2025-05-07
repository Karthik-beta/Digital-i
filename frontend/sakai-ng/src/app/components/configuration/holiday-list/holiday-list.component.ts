import { Component, OnInit, ViewChild } from '@angular/core';
import { Table } from 'primeng/table';
import { LazyLoadEvent } from 'primeng/api';
import { SharedService } from 'src/app/shared.service';
import { MessageService, ConfirmationService } from 'primeng/api';

interface Type {
    name: string;
}

@Component({
  selector: 'app-holiday-list',
  templateUrl: './holiday-list.component.html',
  styleUrl: './holiday-list.component.scss'
})
export class HolidayListComponent implements OnInit {

    @ViewChild('dt') dt: Table;

    holidays: any[] = [];
    selectedHolidays: [];

    display: boolean = false;
    ModalTitle:string="";
    holiday: any;
    types: Type[] | undefined;
    holiday_type: string= '';
    selectedType: Type | null = null;
    id: number | undefined;
    holiday_date: Date | undefined;
    holiday_name: string= '';
    holiday_description: string= '';

    totalRecords: number = 0;
    rowsPerPageOptions: number[] = [10, 20, 30];
    rows: number = this.rowsPerPageOptions[0];
    currentPage: number = 1;
    loading: boolean = true;
    searchQuery: string = '';

    constructor(
            private service:SharedService,
            private messageService: MessageService,
            private confirmationService: ConfirmationService
    ) {}

    ngOnInit() {
        this.types = [
            { name: 'PH' },
            { name: 'FH' }
        ]
    }

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    clear(table: Table) {
        this.searchQuery = '';
        this.dt.reset();
        table.clear();
        this.getHolidayList({ first: 0, rows: this.rows });
    }

    getHolidayList(event: LazyLoadEvent): void {
        this.loading = true;

        const params: any = {
            page: ((event.first || 0) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: event.sortField || '',
            ordering: event.sortField ? `${event.sortOrder === 1 ? '' : '-'}${event.sortField}` : '',
            search: this.searchQuery || '',

            // Add any other query parameters here
          };

          this.service.getHolidayList(params).subscribe({
              next: (response) => {
                  this.holidays = response.results;
                  this.totalRecords = response.count;
              },
              error: (error) => {
                  // Handle error if needed
                  console.error('Error fetching Shifts:', error);
              }
          });

          this.loading = false;
    }

    addClick() {
        this.id = null,
        this.holiday_name = '',
        this.holiday_date = undefined,
        this.selectedType = null,
        this.holiday_description = ''


        this.ModalTitle="Add Holiday";
        this.display=true;
    }

    assignType(selectedType: any) {
        this.holiday_type = selectedType.name;
        console.log(this.holiday_type);
    }

    formatDate(date: Date): string {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based
        const day = String(date.getDate()).padStart(2, '0');

        return `${year}-${month}-${day}`;
    }

    addHoliday() {
        const holidayData = {
            holiday_name: this.holiday_name,
            holiday_date: this.formatDate(this.holiday_date),
            holiday_type: this.selectedType ? this.selectedType.name : '',
            holiday_description: this.holiday_description
        };

        console.log(holidayData);

        this.service.addHolidayList(holidayData).subscribe({
            next: (response) => {
                this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Holiday added successfully' });
                this.getHolidayList({ first: 0, rows: this.rows });
                this.display = false;
            },
            error: (error) => {
                // Handle error if needed
                console.error('Error adding Holiday:', error);
            }
        });
    }

    editClick(item: any) {
        this.id = item.id;
        this.holiday_name = item.holiday_name;
        this.holiday_description = item.holiday_description;

        // Convert date string to Date object
        this.holiday_date = item.holiday_date ? new Date(item.holiday_date) : undefined;

        // Find and set the selected type as an object
        this.selectedType = this.types?.find(type => type.name === item.holiday_type) || null;

        this.ModalTitle="Edit Holiday";
        this.display=true;
        console.log(item);
    }

    updateHoliday() {
        const holidayData = {
            id: this.id,
            holiday_name: this.holiday_name,
            holiday_date: this.formatDate(this.holiday_date),
            holiday_type: this.selectedType ? this.selectedType.name : '',
            holiday_description: this.holiday_description
        };

        console.log(holidayData);

        this.service.updateHolidayList(this.id, holidayData).subscribe({
            next: (response) => {
                this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Holiday updated successfully' });
                this.getHolidayList({ first: 0, rows: this.rows });
                this.display = false;
            },
            error: (error) => {
                // Handle error if needed
                console.error('Error updating Holiday:', error);
            }
        });
    }

}
