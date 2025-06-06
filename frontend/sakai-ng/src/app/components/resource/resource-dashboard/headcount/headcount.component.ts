import { Component } from '@angular/core';

@Component({
  selector: 'app-headcount',
  templateUrl: './headcount.component.html',
  styleUrl: './headcount.component.scss'
})
export class HeadcountComponent {

    combinedLogs: any[] = []; // Initialize as an array
    totalRecords: number = 0;
    rowsPerPageOptions: number[] = [10, 20, 30];
    rows: number = 10;
    currentPage: number = 1;
    loading: boolean = false;

    stateOptions: any[] = [
        { label: 'Show', value: 'true' },
        { label: 'Hide', value: 'false' }
    ];

    showElements: string = 'true';

}
