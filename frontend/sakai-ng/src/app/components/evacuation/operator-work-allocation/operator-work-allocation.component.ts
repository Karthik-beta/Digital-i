import { CommonModule } from '@angular/common';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { CarouselModule } from 'primeng/carousel';
import { TableModule } from 'primeng/table';
import { ChartModule } from 'primeng/chart';
import ChartDataLabels from 'chartjs-plugin-datalabels';
// import { Employee } from 'src/assets/interfaces/operatorworkalocation';

export interface Employee {
  id: number;
  name: string;
  empId: string;
  shopfloor: string;
  assignedMachine: string;
  skillMatrix: string;
  profileImage: string;
}

@Component({
  selector: 'app-operator-work-allocation',
  templateUrl: './operator-work-allocation.component.html',
  styleUrl: './operator-work-allocation.component.scss'
})
export class OperatorWorkAllocationComponent implements OnInit, OnDestroy {

  
  // sections: any[] = [];
  // chartOptions: any;
  // pieChartOptions: any;
  // plugins = [ChartDataLabels];
  // currentDate: string = '';
  // currentTime: string = '';

  sections: any[] = [];
  paginatedSections: any[] = []; // Array of pages (each containing up to 10 sections)
  numVisibleItems: number = 5;
  responsiveOptions: any[] = [];
  chartOptions: any;
  pieChartOptions: any;
  plugins = [ChartDataLabels];
  currentDate: string = '';
  currentTime: string = '';
  timeInterval: any;

  initializeCarouselSettings() {
    this.responsiveOptions = [
      { breakpoint: '1600px', numVisible: 1, numScroll: 1 },
      { breakpoint: '1200px', numVisible: 1, numScroll: 1 },
      { breakpoint: '768px', numVisible: 1, numScroll: 1 },
      { breakpoint: '480px', numVisible: 1, numScroll: 1 }
    ];
  }

  constructor() {}

  ngOnInit(): void {
    this.initializeSections();
    this.paginateSections(); 
    this.initializeCarouselSettings();
    this.initializeChartOptions();
    this.updateTime();

    this.initializeSections();
    this.initializeChartOptions();
    this.updateTime();
    setInterval(() => this.updateTime(), 1000);
  }

  employees: Employee[] = [
    { id: 1, name: "CHANDAN CHETRI", empId: "466", shopfloor: "METAL SHOP", assignedMachine: "MACHINE 1", skillMatrix: "A", profileImage: "download2.jpeg" },
    { id: 2, name: "PANCHANGAM NAVEEN KUMAR", empId: "115", shopfloor: "Steel Waler", assignedMachine: "MACHINE 2", skillMatrix: "B", profileImage: "download3.jpeg" },
    { id: 3, name: "ANIL KUMAR G", empId: "1", shopfloor: "ORT", assignedMachine: "MACHINE 3", skillMatrix: "C", profileImage: "download4.jpeg" },
    { id: 4, name: "RAHUL VERMA", empId: "512", shopfloor: "FABRICATION", assignedMachine: "MACHINE 4", skillMatrix: "A", profileImage: "download5.jpeg" },
    { id: 5, name: "DEEPIKA SINGH", empId: "899", shopfloor: "WELDING", assignedMachine: "MACHINE 5", skillMatrix: "B", profileImage: "download6.jpeg" }
  ];

  updateTime() {
    const now = new Date();
    this.currentDate = now.toLocaleDateString('en-GB').split('/').join('-'); 
    this.currentTime = now.toLocaleTimeString('en-GB', { hour12: false });   
  }

  paginateSections() {

    this.paginatedSections = [];
    for (let i = 0; i < this.sections.length; i += this.numVisibleItems) {
      this.paginatedSections.push({ sections: this.sections.slice(i, i + this.numVisibleItems) });
    }
  }

  

  initializeSections() {
    this.sections = [
  { name: 'Shopfloor 1', pieData: [50, 30, 20], barDataIn: [80, 60, 40], barDataOut: [60, 40, 20] },
  { name: 'Shopfloor 2', pieData: [40, 35, 25], barDataIn: [70, 55, 45], barDataOut: [25, 15, 20] },
  { name: 'Shopfloor 3', pieData: [45, 30, 25], barDataIn: [65, 50, 40], barDataOut: [55, 45, 50] },
  { name: 'Shopfloor 4', pieData: [30, 50, 20], barDataIn: [75, 60, 50], barDataOut: [45, 50, 45] },
  { name: 'Shopfloor 5', pieData: [55, 25, 20], barDataIn: [85, 70, 60], barDataOut: [80, 55, 65] },
  { name: 'Shopfloor 6', pieData: [60, 20, 20], barDataIn: [90, 75, 65], barDataOut: [50, 65, 30] }
];
  }


  initializeChartOptions() {
    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      aspectRatio: 2.3,
      scales: {
        x: {
          ticks: {
            font: {
              size: 8 
            }
          }
        },
        y: {
          ticks: {
            font: {
              size: 10 
            }
          }
        }
      },
      plugins: {
        legend: { display: false },
        datalabels: {
          anchor: 'top', 
          align: 'center', 
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
          backgroundColor: ['#FFD54F', '#FF7043', '#26A69A']
        }
      ]
    };
  }

  getBarChartData(barDataIn: number[], barDataOut: number[]) {
    return {
      labels: ['Shift A', 'Shift B', 'Shift C'],
      datasets: [
        { backgroundColor: '#FF7043', data: barDataIn },
        { backgroundColor: '#26A69A', data: barDataOut }
      ]
    };
  }

  ngOnDestroy(): void {
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
    }
  }
}