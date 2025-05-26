import { Component, OnInit, OnDestroy } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Product } from '../../api/product';
import { ProductService } from '../../service/product.service';
import { debounceTime, distinctUntilChanged, startWith, switchMap } from 'rxjs/operators';
import { Subscription, interval } from 'rxjs';
import { LayoutService } from 'src/app/layout/service/app.layout.service';
import { SharedService } from 'src/app/shared.service';



@Component({
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {

    items!: MenuItem[];

    employees = [
        { type: 'Employee', present: 0, absent: 0 },
        { type: 'Contractor', present: 0, absent: 0 },
        { type: 'Trainee', present: 0, absent: 0 },
        { type: 'Probation', present: 0, absent: 0}
    ]

    chartData: any;

    chartOptions: any;

    subscription!: Subscription;

    presentCount: number=0;

    absentCount: number=0;

    lateEntryCount: number=0;

    earlyExitCount: number=0;

    present_count_last_hour: number=0;

    absent_percentage_increase: number=0;

    frequent_late_arrivals: number=0;

    new_present_since_last_hour: number=0;

    percentage_change_absent_since_last_week: string='';

    byEmployeeType: any = [];

    categoryWiseData: any = [];

    constructor(public layoutService: LayoutService, private service:SharedService) {
        this.subscription = this.layoutService.configUpdate$
        .pipe(debounceTime(25))
        .subscribe((config) => {
            this.initChart();
        });
    }

    ngOnInit() {
        this.initChart();

        this.items = [
            { label: 'Add New', icon: 'pi pi-fw pi-plus' },
            { label: 'Remove', icon: 'pi pi-fw pi-minus' }
        ];

        this.getAttendanceMetrics();
    }

    initChart() {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
        const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

        this.chartData = {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            datasets: [
                {
                    label: 'Present',
                    data: [65, 59, 80, 81, 56, 55, 40],
                    fill: false,
                    backgroundColor: documentStyle.getPropertyValue('--green-700'),
                    borderColor: documentStyle.getPropertyValue('--green-700'),
                    tension: .4
                },
                {
                    label: 'Absent',
                    data: [28, 48, 40, 19, 86, 27, 90],
                    fill: false,
                    backgroundColor: documentStyle.getPropertyValue('--red-600'),
                    borderColor: documentStyle.getPropertyValue('--red-600'),
                    tension: .4
                }
            ]
        };

        this.chartOptions = {
            maintainAspectRatio: false,
            aspectRatio: 1.5,
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: textColorSecondary
                    },
                    grid: {
                        color: surfaceBorder,
                        drawBorder: false
                    }
                },
                y: {
                    ticks: {
                        color: textColorSecondary
                    },
                    grid: {
                        color: surfaceBorder,
                        drawBorder: false
                    }
                }
            }
        };
    }

    private AttendanceMetricSubscription: Subscription;

    getAttendanceMetrics() {
        this.AttendanceMetricSubscription = interval(30000).pipe(
            startWith(0), // emit 0 immediately
            // Use switchMap to switch to a new observable (HTTP request) each time the interval emits
            switchMap(() => this.service.getAttendanceStats()),
            // Use distinctUntilChanged to filter out repeated values
            distinctUntilChanged((prev, curr) => JSON.stringify(prev) === JSON.stringify(curr))
        ).subscribe((data: any) => {
            this.presentCount = data.today.total_present;
            this.new_present_since_last_hour = data.today.new_present_since_last_hour;
            this.absentCount = data.today.total_absent;
            this.percentage_change_absent_since_last_week = data.today.percentage_change_absent_since_last_week;
            this.lateEntryCount = data.today.total_late_entries;
            this.earlyExitCount = data.today.total_early_exits;
            this.present_count_last_hour = data.present_count_last_hour;
            this.absent_percentage_increase = data.absent_percentage_increase;
            this.frequent_late_arrivals = data.frequent_late_arrivals;

            this.byEmployeeType = data.department_data;
            this.categoryWiseData = data.category_data;
            console.log(this.byEmployeeType);
        });
    }

    ngOnDestroy() {
        if (this.subscription) {
            this.subscription.unsubscribe();
        }

        if (this.AttendanceMetricSubscription) {
            this.AttendanceMetricSubscription.unsubscribe();
        }
    }
}
