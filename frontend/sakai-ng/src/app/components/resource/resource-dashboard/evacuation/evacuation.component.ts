import { Component } from '@angular/core';

@Component({
  selector: 'app-evacuation',
  standalone: false,
//   imports: [],
  templateUrl: './evacuation.component.html',
  styleUrl: './evacuation.component.scss'
})
export class EvacuationComponent {


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
