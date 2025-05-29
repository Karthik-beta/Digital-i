import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ChartModule } from 'primeng/chart';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { CommonModule } from '@angular/common';
import {  Employee, Stat, StatusSummary } from '../../interfaces/employee';
import { saveAs } from 'file-saver';
import * as jsPDF from 'jspdf';
import * as docx from 'docx';
import { DropdownModule } from 'primeng/dropdown';
import { FormsModule } from '@angular/forms';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { MenuItem } from 'primeng/api';
import { Chart, registerables , ChartData, ChartOptions} from 'chart.js';


@Component({
  selector: 'app-emp-strength',
  templateUrl: './emp-strength.component.html',
  styleUrl: './emp-strength.component.css'
})
export class EmpStrengthComponent implements OnInit, OnDestroy {

  plugins = [ChartDataLabels];
  activeLeaveType: string = 'EL';
  currentDate: string = '';
  currentTime: string = '';
  timeInterval: any;

  statuses: StatusSummary[] = [
    { count: 12, label: 'Present', icon: 'pi pi-user', color: '#4CAF50' },
    { count: 20, label: 'Absent', icon: 'pi pi-user-minus', color: '#F44336' },
    { count: 0, label: 'Late Arrival', icon: 'pi pi-clock', color: '#FFC107' },
    { count: 0, label: 'Early Leave', icon: 'pi pi-arrow-right', color: '#03A9F4' },
    { count: 0, label: 'Missed Punch', icon: 'pi pi-ban', color: '#FF5722' },
    { count: 0, label: 'Half Day', icon: 'pi pi-calendar', color: '#00BCD4' },
    { count: 0, label: 'Over Time', icon: 'pi pi-hourglass', color: '#FF9800' }

  ];

  getRandomColor(): string {
    const colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A6', '#FFC300', '#8E44AD', '#1ABC9C'];
    return colors[Math.floor(Math.random() * colors.length)];
  }
  stats: Stat[] = [
    { title: 'Live Headcount', value: 0, icon: 'pi pi-users', color: '#2196F3' },
    { title: 'Total Check In', value: 134, icon: 'pi pi-sign-in', color: '#4CAF50' },
    { title: 'Total Check Out', value: 36, icon: 'pi pi-sign-out', color: '#FF9800' }
  ];

  activeBarChartData: ChartData<'bar'> = {
    labels: [''],
    datasets: [
      {
        label: 'Check-in',
        backgroundColor: '#4CAF50', // Green color
        borderColor: '#4CAF50',
        borderWidth: 1,
        data: [260], // Example data for Check-in
        barPercentage: 0.6, // Reduce individual bar width
        categoryPercentage: 0.7, // Reduce category width
      },
      {
        label: 'Check-out',
        backgroundColor: '#FF5252', // Red color
        borderColor: '#FF5252',
        borderWidth: 1,
        data: [140], // Example data for Check-out
        barPercentage: 0.6, // Reduce individual bar width
        categoryPercentage: 0.7, // Reduce category width
      },
    ],
  };

  activeBarChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
    },
    scales: {
      x: {
        stacked: false,
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        max: 400,
        stacked: false,
      },
    },
  };



  buttons = ['Active', 'Present', 'Absent', 'Late', 'Early', 'MP', 'HD', 'OT', 'Leave', 'OD'];


  colorMap: { [key: string]: string } = {
    'Active': '#3498db',
    'Present': '#2ecc71',
    'Absent': '#e74c3c',
    'Late': '#f39c12',
    'Early': '#f1c40f',
    'MP': '#9b59b6',
    'HD': '#e91e63',
    'OT': '#1abc9c',
    'Leave': '#95a5a6',
    'OD': '#795548'
  };

  chartDataSets: { [key: string]: number[] } = {
    'Active': [200, 300, 400, 450, 350, 250, 300, 400, 450, 350, 300, 250],
    'Present': [180, 290, 380, 420, 340, 240, 290, 390, 440, 340, 290, 240],
    'Absent': [50, 70, 100, 90, 80, 60, 70, 110, 120, 90, 80, 70],
    'Late': [30, 50, 40, 45, 35, 25, 30, 40, 45, 35, 30, 25],
    'Early': [20, 30, 25, 35, 30, 20, 25, 30, 35, 30, 25, 20],
    'MP': [10, 15, 12, 18, 14, 9, 13, 17, 16, 14, 11, 8],
    'HD': [5, 10, 7, 9, 6, 4, 8, 11, 10, 7, 5, 3],
    'OT': [25, 40, 35, 50, 45, 30, 40, 55, 50, 40, 35, 30],
    'Leave': [15, 20, 18, 22, 17, 12, 19, 24, 21, 18, 16, 10],
    'OD': [8, 12, 10, 14, 11, 7, 13, 16, 14, 10, 9, 5]
  };

  selectedCategory: string = 'Active';


  barChartData = this.getChartData('Active');

  barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#495057' }
      },datalabels: {
        anchor: 'start',
        align: 'top',
        color: '#fff',
        font: { weight: 'bold', size: 11 },
        formatter: (value: number) => value
      }
    },
    scales: {
      x: {
        ticks: { color: '#495057' },
        grid: { color: 'rgba(200, 200, 200, 0.2)' }
      },
      y: {
        ticks: { color: '#495057' },
        grid: { color: 'rgba(200, 200, 200, 0.2)' }
      }
    }
  };


  getChartData(category: string) {
    const color = this.colorMap[category] || '#3498db';
    return {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      datasets: [
        {
          label: category,
          data: this.chartDataSets[category] || [],
          backgroundColor: color,
          borderColor: color,
          borderWidth: 1,
          barThickness: 35,
        }
      ]
    };
  }


  updateChartData(category: string) {
    this.selectedCategory = category;
    this.barChartData = this.getChartData(category);
  }


  getButtonClass(button: string): string {
    const baseClass = 'side-btn';
    const colorClass = `b-${button.toLowerCase()}`;
    const activeClass = button === this.selectedCategory ? 'active-btn' : '';
    return `${baseClass} ${colorClass} ${activeClass}`;
  }

  employees: Employee[] = [
    { name: 'CHANDAN CHETTRI', empId: 466, image: 'download3.jpeg', leaveType: 'EL' },
    { name: 'CHANGAM NAVEEN', empId: 115, image: 'download4.jpeg', leaveType: 'CL' },
    { name: 'ANIL KUMAR G', empId: 141, image: 'download5.jpeg', leaveType: 'Medical' },
    { name: 'PRIYA SHARMA', empId: 289, image: 'download6.jpeg', leaveType: 'SL' },
    { name: 'RAHUL VERMA', empId: 512, image: 'download3.jpeg', leaveType: 'LOP' },
    { name: 'SNEHA MISHRA', empId: 634, image: 'download6.jpeg', leaveType: 'OD' },
    { name: 'ARJUN KAPOOR', empId: 777, image: 'download2.jpeg', leaveType: 'MP' },
    { name: 'DEEPIKA SINGH', empId: 899, image: 'download6.jpeg', leaveType: 'HD' },
    { name: 'VIKRAM CHAUHAN', empId: 321, image: 'download.jpeg', leaveType: 'OT' },
    { name: 'AISHWARYA ROY', empId: 225, image: 'download6.jpeg', leaveType: 'EL' },
    { name: 'ROHAN DAS', empId: 601, image: 'download5.jpeg', leaveType: 'CL' },
    { name: 'MEENA AGARWAL', empId: 410, image: 'download6.jpeg', leaveType: 'Medical' },
    { name: 'SUMIT KUMAR', empId: 558, image: 'download4.jpeg', leaveType: 'SL' },
    { name: 'TINA KAPOOR', empId: 909, image: 'download6.jpeg', leaveType: 'LOP' },
    { name: 'GAURAV SHARMA', empId: 777, image: 'download4.jpeg', leaveType: 'OD' },
    { name: 'KARAN MEHTA', empId: 122, image: 'download3.jpeg', leaveType: 'MP' },
    { name: 'RITA GUPTA', empId: 305, image: 'download6.jpeg', leaveType: 'HD' },
    { name: 'AMIT JOSHI', empId: 718, image: 'download2.jpeg', leaveType: 'OT' }
  ];


  constructor(private cdr: ChangeDetectorRef) {
    Chart.register(...registerables, ChartDataLabels);
  }

  ngOnInit(): void {
    Chart.register(ChartDataLabels);
    this.updateTime();

    this.timeInterval = setInterval(() => {
      this.updateTime();
      this.cdr.detectChanges(); // Detect changes without reloading the entire component
    }, 1000);
  }

  updateTime() {
    const now = new Date();
    this.currentDate = now.toLocaleDateString('en-GB').split('/').join('-');
    this.currentTime = now.toLocaleTimeString('en-GB', { hour12: false });
  }

  ngOnDestroy(): void {
    if (this.timeInterval) {
      clearInterval(this.timeInterval); // Clear interval to prevent memory leaks
    }
  }

  filteredEmployees: Employee[] = this.employees.filter(emp => emp.leaveType === this.activeLeaveType);

  leaveChartData = {
    labels: ['EL', 'CL', 'SL', 'Medical', 'LOP', 'OD'],
    datasets: [
      {
        data: [10, 15, 8, 12, 7, 6],
        backgroundColor: ['#007ad9', '#ffa726', '#8e44ad', '#27ae60', '#c0392b', '#3498db'],
        hoverBackgroundColor: ['#0056a3', '#ff9800', '#6c3483', '#1e8449', '#922b21', '#217dbb']
      }
    ]
  };

  getLeaveColor(leaveType: string): string {
    const index = this.leaveChartData.labels.indexOf(leaveType);
    return index !== -1 ? this.leaveChartData.datasets[0].backgroundColor[index] : '#6c757d';
  }


  filterEmployees(leaveType: string): void {
    this.activeLeaveType = leaveType;
    this.filteredEmployees = this.employees.filter(emp => emp.leaveType === leaveType);
  }

  donutChartOptions: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      datalabels: {
        color: 'white',
        font: { weight: 'bold', size: 14 },
        formatter: (value: number, ctx) => {
          return value > 0 ? value : ''; // Show only non-zero values
        },
      },
    },
  };

  // Custom plugin to display total sum inside the donut chart
  plugin = [
    ChartDataLabels as any,
    {
      id: 'totalSum',
      beforeDraw: (chart: Chart<'doughnut' | 'bar' | 'line'>) => {
        // Get the chart type directly from the chart instance
        const chartType = chart.config.options?.indexAxis
        console.log(chartType)

        if (chartType === 'y' || chartType === 'x') {
          return;
        }

        const ctx = chart.ctx;
        const width = chart.width;
        const height = chart.height;
        ctx.restore();

        // Calculate total sum of values
        const sum = (chart.data.datasets[0].data as number[]).reduce(
          (acc, val) => acc + val,
          0
        );

        // Styling for text
        ctx.font = 'bold 16px Arial';
        ctx.fillStyle = 'black';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Display total sum in center of chart
        ctx.fillText(sum.toString(), width / 2, height / 2);
        ctx.save();
      },
    },
  ];


}
