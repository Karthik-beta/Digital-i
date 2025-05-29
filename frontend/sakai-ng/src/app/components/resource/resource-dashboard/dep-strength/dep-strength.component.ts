import { CommonModule } from '@angular/common';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CardModule } from 'primeng/card';
import { ChartModule } from 'primeng/chart';
import { ButtonModule } from 'primeng/button';
import { CarouselModule } from 'primeng/carousel';
import ChartDataLabels from 'chartjs-plugin-datalabels';

@Component({
  selector: 'app-dep-strength',
  templateUrl: './dep-strength.component.html',
  styleUrl: './dep-strength.component.css'
})
export class DepStrengthComponent implements OnInit, OnDestroy {

  sections: any[] = [];
  paginatedSections: any[] = []; // Array of pages (each containing up to 10 sections)
  numVisibleItems: number = 18;
  responsiveOptions: any[] = [];
  chartOptions: any;
  pieChartOptions: any;
  plugins = [ChartDataLabels];
  currentDate: string = '';
  currentTime: string = '';

  constructor() {}

  ngOnInit(): void {
    this.initializeSections();
    this.paginateSections();
    this.initializeCarouselSettings();
    this.initializeChartOptions();
    this.updateTime();
    setInterval(() => this.updateTime(), 1000);
  }


  ngOnDestroy(): void {}

  updateTime() {
    const now = new Date();
    console.log('time updated')
    this.currentDate = now.toLocaleDateString('en-GB').split('/').join('-');
    this.currentTime = now.toLocaleTimeString('en-GB', { hour12: false });
  }
  initializeSections() {
    this.sections = [
      { name: 'Operations', pieData: [50, 30, 20], barDataIn: [80, 60, 40], barDataOut: [60, 40, 20] },
      { name: 'Admin', pieData: [40, 35, 25], barDataIn: [70, 55, 45], barDataOut: [25, 15, 20] },
      { name: 'HR', pieData: [45, 30, 25], barDataIn: [65, 50, 40], barDataOut: [55, 45, 50] },
      { name: 'Store', pieData: [30, 50, 20], barDataIn: [75, 60, 50], barDataOut: [45, 50, 45] },
      { name: 'Purchase', pieData: [55, 25, 20], barDataIn: [85, 70, 60], barDataOut: [80, 55, 65] },
      { name: 'Accounts', pieData: [60, 20, 20], barDataIn: [90, 75, 65], barDataOut: [50, 65, 30] },
      { name: 'Metal Shopfloor', pieData: [35, 40, 25], barDataIn: [80, 65, 55], barDataOut: [80, 55, 65] },
      { name: 'ORT Shopfloor', pieData: [25, 50, 25], barDataIn: [70, 55, 45], barDataOut: [70, 45, 55] },
      { name: 'Metal Waller Shopfloor', pieData: [30, 45, 25], barDataIn: [85, 70, 60], barDataOut: [70, 85, 60] },
      { name: 'Welding Shopfloor', pieData: [40, 35, 25], barDataIn: [75, 60, 50], barDataOut: [60, 75, 50] },
      { name: 'Design', pieData: [50, 30, 20], barDataIn: [80, 65, 55], barDataOut: [65, 55, 30] },
      { name: 'Logistics', pieData: [45, 35, 20], barDataIn: [85, 70, 60], barDataOut: [75, 50, 55] },
      { name: 'Quality Control', pieData: [30, 50, 20], barDataIn: [80, 65, 55], barDataOut: [60, 45, 40] },
      { name: 'Maintenance', pieData: [55, 30, 15], barDataIn: [90, 75, 65], barDataOut: [85, 70, 60] },
      { name: 'IT Support', pieData: [35, 40, 25], barDataIn: [70, 55, 45], barDataOut: [55, 40, 35] },
      { name: 'Security', pieData: [25, 50, 25], barDataIn: [65, 50, 40], barDataOut: [45, 35, 30] },
      { name: 'Production', pieData: [50, 25, 25], barDataIn: [95, 80, 70], barDataOut: [85, 75, 65] },
      { name: 'R&D', pieData: [40, 35, 25], barDataIn: [75, 60, 50], barDataOut: [55, 45, 40] },
      { name: 'Legal', pieData: [30, 45, 25], barDataIn: [85, 70, 55], barDataOut: [75, 60, 50] },
      { name: 'Procurement', pieData: [45, 30, 25], barDataIn: [80, 65, 55], barDataOut: [70, 50, 45] },
      { name: 'Customer Support', pieData: [50, 25, 25], barDataIn: [90, 75, 60], barDataOut: [65, 55, 45] },
      { name: 'Marketing', pieData: [55, 30, 15], barDataIn: [85, 70, 60], barDataOut: [75, 65, 55] },
      { name: 'Sales', pieData: [40, 35, 25], barDataIn: [75, 60, 50], barDataOut: [55, 40, 35] },
      { name: 'Packaging', pieData: [35, 45, 20], barDataIn: [70, 55, 45], barDataOut: [60, 50, 40] },
      { name: 'Assembly Line', pieData: [45, 35, 20], barDataIn: [85, 70, 60], barDataOut: [75, 55, 50] }

    ];
  }

  paginateSections() {
    this.paginatedSections = [];
    for (let i = 0; i < this.sections.length; i += 18) {
      this.paginatedSections.push({ sections: this.sections.slice(i, i + 18) });
    }
  }

  initializeCarouselSettings() {
    this.responsiveOptions = [
      { breakpoint: '1600px', numVisible: 1, numScroll: 1 },
      { breakpoint: '1200px', numVisible: 1, numScroll: 1 },
      { breakpoint: '768px', numVisible: 1, numScroll: 1 },
      { breakpoint: '480px', numVisible: 1, numScroll: 1 }
    ];
  }

  initializeChartOptions() {
    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        datalabels: {
          anchor: 'end',
          align: 'top',
          font: { weight: 'bold', size: 8 },
          formatter: (value: number) => value
        }
      }
    };

    this.pieChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true },
        datalabels: {
          color: '#fff',
          font: { weight: 'bold', size: 12 },
          formatter: (value: number) => value
        }
      }
    };
  }

  getPieChartData(pieData: number[]) {
    return {
      datasets: [
        {
          data: pieData,
          backgroundColor: ['#007bff', '#28a745', '#dc3545']
        }
      ]
    };
  }

  getBarChartData(barDataIn: number[], barDataOut: number[]) {
    return {
      labels: ['Shift A', 'Shift B', 'Shift C'],
      datasets: [
        { backgroundColor: '#FFD700', data: barDataIn },
        { backgroundColor: '#B2EBF2', data: barDataOut }
      ]
    };
  }
}
