import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ChartModule } from 'primeng/chart';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { CommonModule } from '@angular/common';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Chart, registerables , ChartData, ChartOptions} from 'chart.js';
// import { Employee } from 'src/assets/interfaces/empintervalstrength';

export interface Employee {
  name: string;
  empId: number;
  image: string;
  leaveType: string;
  date: string; 
  status: string;
}

@Component({
  selector: 'app-emp-interval-strength',
  templateUrl: './emp-interval-strength.component.html',
  styleUrl: './emp-interval-strength.component.scss'
})
export class EmpIntervalStrengthComponent implements OnInit, OnDestroy {

  plugins = [ChartDataLabels]; 
  activeLeaveType: string = 'EL';
  currentDate: string = '';
  currentTime: string = '';
  timeInterval: any;

  monthlyFilteredEmployees: Employee[] = [];
  lastThityDaysFilteredEmployees: Employee[] = [];
  lastSevenDaysFilteredEmployees: Employee[] = [];
 
  buttons = ['Active', 'Present', 'Absent', 'Late', 'Early', 'MP', 'HD', 'OT', 'Leave', 'OD'];

  colorMap: { [key: string]: string } = {
    'Active': ' #3498db',  
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

  daysCartDataSets: { [key: string]: number[] } = {
    'Active': [200, 300, 400, 450, 350, 250, 300, 400, 450, 350, 300, 250, 410, 470, 360, 320, 270, 380, 420, 390, 460, 340, 330, 310, 480, 370, 360, 320, 280, 300],
    'Present': [180, 290, 380, 420, 340, 240, 290, 390, 440, 340, 290, 240, 380, 440, 330, 310, 260, 370, 400, 390, 450, 320, 310, 280, 470, 350, 340, 300, 260, 280],
    'Absent': [50, 70, 100, 90, 80, 60, 70, 110, 120, 90, 80, 70, 120, 130, 95, 85, 75, 140, 150, 130, 110, 100, 90, 80, 160, 130, 120, 110, 90, 100],
    'Late': [30, 50, 40, 45, 35, 25, 30, 40, 45, 35, 30, 25, 50, 55, 40, 35, 30, 60, 65, 55, 50, 45, 40, 35, 70, 55, 50, 40, 30, 35],
    'Early': [20, 30, 25, 35, 30, 20, 25, 30, 35, 30, 25, 20, 35, 40, 35, 30, 25, 50, 55, 40, 30, 25, 20, 18, 60, 45, 40, 35, 25, 20],
    'MP': [10, 15, 12, 18, 14, 9, 13, 17, 16, 14, 11, 8, 19, 18, 16, 13, 9, 21, 23, 19, 16, 14, 10, 9, 25, 20, 18, 15, 12, 10],
    'HD': [5, 10, 7, 9, 6, 4, 8, 11, 10, 7, 5, 3, 13, 12, 9, 6, 4, 14, 15, 12, 9, 7, 5, 3, 16, 12, 10, 9, 6, 5],
    'OT': [25, 40, 35, 50, 45, 30, 40, 55, 50, 40, 35, 30, 60, 55, 45, 40, 35, 70, 75, 65, 60, 50, 45, 40, 80, 65, 55, 50, 40, 35],
    'Leave': [15, 20, 18, 22, 17, 12, 19, 24, 21, 18, 16, 10, 27, 24, 21, 19, 12, 30, 35, 28, 25, 20, 18, 12, 38, 25, 24, 22, 18, 15],
    'OD': [8, 12, 10, 14, 11, 7, 13, 16, 14, 10, 9, 5, 18, 16, 12, 10, 6, 20, 22, 18, 14, 10, 9, 6, 24, 18, 14, 12, 10, 8]
};


  sevenDaysChartDataSets: { [key: string]: number[] } = {
    'Active': [220, 310, 410, 470, 360, 260, 320],
    'Present': [190, 280, 390, 430, 350, 250, 300],
    'Absent': [60, 80, 110, 95, 85, 65, 80],
    'Late': [35, 55, 45, 50, 40, 30, 35],
    'Early': [25, 35, 30, 40, 35, 25, 30],
    'MP': [12, 18, 15, 20, 16, 11, 14],
    'HD': [7, 12, 9, 11, 8, 5, 10],
    'OT': [30, 45, 40, 55, 50, 35, 45],
    'Leave': [18, 23, 21, 25, 20, 15, 22],
    'OD': [10, 14, 12, 16, 13, 9, 15],

  };

  monthlyChartDataSets: { [key: string]: number[] } = {
    'Active': [230, 320, 400, 480, 370, 270, 330, 420, 460, 370, 330, 280],
    'Present': [200, 290, 380, 440, 360, 260, 310, 390, 450, 340, 320, 270],
    'Absent': [70, 85, 120, 100, 90, 70, 85, 130, 140, 100, 90, 80],
    'Late': [40, 60, 50, 55, 45, 35, 40, 55, 60, 45, 40, 35],
    'Early': [30, 40, 35, 45, 40, 30, 35, 40, 45, 40, 35, 30],
    'MP': [15, 20, 17, 22, 18, 12, 16, 21, 20, 18, 15, 10],
    'HD': [9, 14, 11, 13, 10, 7, 12, 15, 14, 11, 8, 5],
    'OT': [35, 50, 45, 60, 55, 40, 50, 65, 60, 50, 45, 40],
    'Leave': [20, 25, 23, 28, 22, 17, 25, 30, 27, 24, 21, 15],
    'OD': [12, 16, 14, 18, 15, 10, 17, 20, 18, 14, 12, 8],
  };


  yearSelectedCategory: string = 'Active';
  monthSelectedCategory: string = 'Active';
  daysSelectedCategory: string = 'Active';

  
  yearBarChartData = this.getYearChartData('Active');
  monthBarChartData = this.getMonthChartData('Active');
  daysBarChartData = this.getDaysChartData('Active');

  barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    aspectRatio: 2.2,
    plugins: {
      legend: {
        labels: { color: '#495057' }
      },datalabels: {
        anchor: 'top', 
        align: 'center', 
        color: '#fff', 
        font: { weight: 'bold', size: 10 },
        formatter: (value: number) => value 
      }
    },
    scales: {
      x: {
        ticks: { color: '#495057', font: { size: 10 } },
        grid: { color: 'rgba(200, 200, 200, 0.2)' },
      },
      y: {
        ticks: { color: '#495057' },
        grid: { color: 'rgba(200, 200, 200, 0.2)' }
        
      }
    }
  };

  
  getYearChartData(category: string) {
    const color = this.colorMap[category] || '#3498db'; 
    return {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      datasets: [
        {
          label: category,
          data: this.monthlyChartDataSets[category] || [],
          backgroundColor: color,
          borderColor: color,
          borderWidth: 1,
          barThickness: 35,
        }
      ]
    };
  }
  getMonthChartData(category: string) {
    const color = this.colorMap[category] || '#3498db'; 
    return {
      labels: ['D30', 'D29', 'D28', 'D27', 'D26', 'D25', 'D24', 'D23', 'D22', 'D21', 'D20', 'D19', 'D18','D17', 'D16', 'D15', 'D14', 'D13', 'D12', 'D11', 'D10', 'D9', 'D8', 'D7', 'D6', 'D5', 'D4','D3','D2','D1'],
      datasets: [
        {
          label: category,
          data: this.daysCartDataSets[category] || [],
          backgroundColor: color,
          borderColor: color,
          borderWidth: 1,
          barThickness: 15,
        }
      ]
    };
  }
  getDaysChartData(category: string) {
    const color = this.colorMap[category] || '#3498db'; 
    return {
      labels: ['D7', 'D6', 'D5', 'D4','D3','D2','D1'],
      datasets: [
        {
          label: category,
          data: this.daysCartDataSets[category] || [],
          backgroundColor: color,
          borderColor: color,
          borderWidth: 1,
          barThickness: 35,
        }
      ]
    };
  }

  
  updateYearChartData(category: string) {
    this.yearSelectedCategory = category;
    this.yearBarChartData = this.getYearChartData(category);
  }
  updateMonthChartData(category: string) {
    this.monthSelectedCategory = category;
    this.monthBarChartData = this.getMonthChartData(category);
  }
  updateDaysChartData(category: string) {
    this.daysSelectedCategory = category;
    this.daysBarChartData = this.getDaysChartData(category);
  }

  
  getButtonClass(button: string): string {
    const baseClass = 'side-btn';
    const colorClass = `b-${button.toLowerCase()}`;
    const activeClass = button === this.yearSelectedCategory ? 'active-btn' : ''; 
    return `${baseClass} ${colorClass} ${activeClass}`;
  }

  employees: Employee[] = [
    { name: 'CHANDAN CHETTRI', empId: 466, image: 'download4.jpeg', leaveType: 'EL', date: '2025-03-12', status: 'Active' },
    { name: 'AISHWARYA ROY', empId: 225, image: 'download6.jpeg', leaveType: 'CL', date: '2025-03-10', status: 'Present' },
    { name: 'RAHUL VERMA', empId: 512, image: 'download.jpeg', leaveType: 'LOP', date: '2025-03-07', status: 'Absent' },
    { name: 'DEEPIKA SINGH', empId: 899, image: 'download6.jpeg', leaveType: 'SL', date: '2025-02-28', status: 'Late' },
    { name: 'VIKRAM CHAUHAN', empId: 321, image: 'download2.jpeg', leaveType: 'OD', date: '2025-03-14', status: 'Active' },
    { name: 'ROHAN SHARMA', empId: 678, image: 'download3.jpeg', leaveType: 'MP', date: '2025-03-13', status: 'MP' },
    { name: 'PRIYA MEHTA', empId: 345, image: 'download6.jpeg', leaveType: 'OD', date: '2025-03-11', status: 'OD' },
    { name: 'ANITA KAPOOR', empId: 789, image: 'download6.jpeg', leaveType: 'Leave', date: '2025-03-09', status: 'Medical' },
    { name: 'RAJAT KUMAR', empId: 234, image: 'download4.jpeg', leaveType: 'HD', date: '2025-03-08', status: 'HD' },
    { name: 'SONALI GUPTA', empId: 555, image: 'download6.jpeg', leaveType: 'OT', date: '2025-03-06', status: 'OT' },
    { name: 'ARJUN NAIR', empId: 412, image: 'download5.jpeg', leaveType: 'Early', date: '2025-03-05', status: 'Early' }
  ];


  getFilteredEmployees() {
    const today = new Date();
  
    this.employees.forEach(emp => {
      const empDate = new Date(emp.date);
      const diffTime = today.getTime() - empDate.getTime();
      const diffDays = diffTime / (1000 * 3600 * 24);
  
      // Push employees into respective lists
      if (diffDays <= 30) {
        this.monthlyFilteredEmployees.push(emp);
      }
      if(diffDays >= 30 && diffDays <= 7){
        this.lastThityDaysFilteredEmployees.push(emp);
      }
      if (diffDays >= 7) {
        this.lastSevenDaysFilteredEmployees.push(emp);
      }
    });
  
    // return { monthly, last30Days, last7Days };
  }
  
  constructor(private cdr: ChangeDetectorRef) {
    Chart.register(...registerables, ChartDataLabels);
  }

  ngOnInit(): void {
    Chart.register(ChartDataLabels);
    this.updateTime();
    this.getFilteredEmployees();

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