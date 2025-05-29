import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { CarouselModule } from 'primeng/carousel';
import { ChartModule } from 'primeng/chart';
import ChartDataLabels from 'chartjs-plugin-datalabels';

@Component({
  selector: 'app-food-court',
  templateUrl: './food-court.component.html',
  styleUrl: './food-court.component.css'
})
export class FoodCourtComponent implements OnInit, OnDestroy {

  sections: any[] = [];
  paginatedSections: any[] = []; // Array of pages (each containing up to 10 sections)
  numVisibleItems: number = 12;
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
      { name: 'Shop 1', pieData: [50, 30, 20], barDataIn: [80, 60, 40], barDataOut: [60, 40, 20] },
      { name: 'Shop 2', pieData: [40, 35, 25], barDataIn: [70, 55, 45], barDataOut: [25, 15, 20] },
      { name: 'Shop 3', pieData: [45, 30, 25], barDataIn: [65, 50, 40], barDataOut: [55, 45, 50] },
      { name: 'Shop 4', pieData: [30, 50, 20], barDataIn: [75, 60, 50], barDataOut: [45, 50, 45] },
      { name: 'Shop 5', pieData: [55, 25, 20], barDataIn: [85, 70, 60], barDataOut: [80, 55, 65] },
      { name: 'Shop 6', pieData: [60, 20, 20], barDataIn: [90, 75, 65], barDataOut: [50, 65, 30] },
      { name: 'Shop 7', pieData: [35, 40, 25], barDataIn: [80, 65, 55], barDataOut: [80, 55, 65] },
      { name: 'Shop 8', pieData: [25, 50, 25], barDataIn: [70, 55, 45], barDataOut: [70, 45, 55] },
      { name: 'Shop 9', pieData: [30, 45, 25], barDataIn: [85, 70, 60], barDataOut: [70, 85, 60] },
      { name: 'Shop 10', pieData: [40, 35, 25], barDataIn: [75, 60, 50], barDataOut: [60, 75, 50] },
      { name: 'Shop 11', pieData: [50, 30, 20], barDataIn: [80, 65, 55], barDataOut: [65, 55, 30] },
      { name: 'Shop 12', pieData: [45, 35, 20], barDataIn: [85, 70, 60], barDataOut: [75, 50, 55] },
      { name: 'Shop 13', pieData: [30, 50, 20], barDataIn: [80, 65, 55], barDataOut: [60, 45, 40] },
      { name: 'Shop 14', pieData: [55, 30, 15], barDataIn: [90, 75, 65], barDataOut: [85, 70, 60] },
      { name: 'Shop 15', pieData: [35, 40, 25], barDataIn: [70, 55, 45], barDataOut: [55, 40, 35] },
      { name: 'Shop 16', pieData: [25, 50, 25], barDataIn: [65, 50, 40], barDataOut: [45, 35, 30] },
      { name: 'Shop 17', pieData: [50, 25, 25], barDataIn: [95, 80, 70], barDataOut: [85, 75, 65] },
      { name: 'Shop 18', pieData: [40, 35, 25], barDataIn: [75, 60, 50], barDataOut: [55, 45, 40] },
      { name: 'Shop 19', pieData: [30, 45, 25], barDataIn: [85, 70, 55], barDataOut: [75, 60, 50] },
      { name: 'Shop 20', pieData: [45, 30, 25], barDataIn: [80, 65, 55], barDataOut: [70, 50, 45] },
      { name: 'Shop 21', pieData: [50, 25, 25], barDataIn: [90, 75, 60], barDataOut: [65, 55, 45] },
      { name: 'Shop 22', pieData: [55, 30, 15], barDataIn: [85, 70, 60], barDataOut: [75, 65, 55] },
      { name: 'Shop 23', pieData: [40, 35, 25], barDataIn: [75, 60, 50], barDataOut: [55, 40, 35] },
      { name: 'Shop 24', pieData: [35, 45, 20], barDataIn: [70, 55, 45], barDataOut: [60, 50, 40] },
      { name: 'Shop 25', pieData: [45, 35, 20], barDataIn: [85, 70, 60], barDataOut: [75, 55, 50] }

    ];
  }

  paginateSections() {
    this.paginatedSections = [];
    for (let i = 0; i < this.sections.length; i += 12) {
      this.paginatedSections.push({ sections: this.sections.slice(i, i + 12) });
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
      labels: ['BreakFast', 'Lunch', 'Dinner'],
      datasets: [
        { backgroundColor: '#dc3545', data: barDataIn },
        { backgroundColor: '#007bff', data: barDataOut }
      ]
    };
  }
}
