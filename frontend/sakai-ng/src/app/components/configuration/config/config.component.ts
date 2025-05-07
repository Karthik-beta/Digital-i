import { Component, ViewChildren, QueryList, OnInit, OnDestroy } from '@angular/core';
import { SharedService } from 'src/app/shared.service';
import { EventemitterService } from 'src/app/service/eventemitter/eventemitter.service';
import { Observable, Subscription } from 'rxjs';
import { interval } from 'rxjs';
import { map, switchMap, distinctUntilChanged, startWith } from 'rxjs/operators';
// import { Panel } from 'primeng/panel';

@Component({
  selector: 'app-config',
  standalone: false,
//   imports: [],
  templateUrl: './config.component.html',
  styleUrl: './config.component.scss'
})
export class ConfigComponent implements OnInit, OnDestroy {

    collapsed: boolean = true;

    constructor(private service:SharedService, private eventEmitterService:EventemitterService) { }

    ngOnInit(): void {
        this.eventSubscription = this.eventEmitterService.invokeGetUpdatedAtList.subscribe(() => {
            this.getUpdatedAtList();
        });
        this.getUpdatedAtList();
    }

    company: string = '';
    location: string = '';
    department: string = '';
    designation: string = '';
    division: string = '';
    subDivision: string = '';
    shopfloor: string = '';
    shift: string = '';

    private eventSubscription: Subscription;
    private UpdatedAtListSubscription: Subscription;

    getUpdatedAtList() {
        this.UpdatedAtListSubscription = interval(60000).pipe(
            startWith(0),// emit 0 immediately
            // Use switchMap to switch to a new observable (HTTP request) each time the interval emits
            switchMap(() => this.service.getUpdatedat()),
            // Use distinctUntilChanged to filter out repeated values
            distinctUntilChanged((prev, curr) => JSON.stringify(prev) === JSON.stringify(curr))
            ).subscribe((data: any) => {
            // Extract individual fields from data and assign them to variables
            const { Company, Location, Department, Designation, Division, SubDivision, Shopfloor, Shift } = data;
            // Assign extracted fields to component properties or variables
            this.company = Company;
            this.location = Location;
            this.department = Department;
            this.designation = Designation;
            this.division = Division;
            this.subDivision = SubDivision;
            this.shopfloor = Shopfloor;
            this.shift = Shift;
        });
    }

    ngOnDestroy() {

        this.eventSubscription.unsubscribe();

        // Unsubscribe from the interval observable
        if (this.UpdatedAtListSubscription) {
            this.UpdatedAtListSubscription.unsubscribe();
        }
    }
}
