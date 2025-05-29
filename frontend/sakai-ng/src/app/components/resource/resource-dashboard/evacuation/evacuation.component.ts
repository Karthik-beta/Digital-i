import { CommonModule } from '@angular/common';
import { Component, OnInit, OnDestroy,  ViewChild, ElementRef, ChangeDetectorRef  } from '@angular/core';
import { CardModule } from 'primeng/card';
import { ChartModule } from 'primeng/chart';
import { ChartData, ChartOptions } from 'chart.js';
// import { Employee } from '../../interfaces/employee';
import ChartDataLabels from 'chartjs-plugin-datalabels';
// import Chart from 'chart.js/auto';
import { Chart,ChartType, registerables} from 'chart.js';

@Component({
  selector: 'app-evacuation',
  templateUrl: './evacuation.component.html',
  styleUrl: './evacuation.component.css'
})
export class evacuationComponent implements OnInit, OnDestroy{

  @ViewChild('departmentChart', { static: true }) chartRef!: ElementRef<HTMLCanvasElement>;
  chart!: Chart;

  departmentData: { name: string; strength: number }[] = [];
  displayedData: { name: string; strength: number }[] = [];
  chartOption: any;
  currentPage: number = 0;
  pageSize: number = 15;
  totalPages: number = 1;
  autoSlideInterval: any;
  currentDate: string = '';
  currentTime: string = '';
  timeInterval: any;

  constructor(private cdr: ChangeDetectorRef) {
    Chart.register(...registerables, ChartDataLabels);
  }

  updateTime() {
    const now = new Date();
    this.currentDate = now.toLocaleDateString('en-GB').split('/').join('-');
    this.currentTime = now.toLocaleTimeString('en-GB', { hour12: false });
  }

  calculateDepartmentStrength(): void {
    const departmentCounts = this.countDepartment();
    this.departmentData = Object.keys(departmentCounts).map(dept => ({
      name: dept,
      strength: departmentCounts[dept]
    }));

    this.totalPages = Math.ceil(this.departmentData.length / this.pageSize);
    this.updateChart();
  }

  updateChart(): void {
    const startIndex = this.currentPage * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    this.displayedData = this.departmentData.slice(startIndex, endIndex);

    if (this.chart) {
      this.chart.destroy(); // Destroy the previous chart before re-creating it
    }

    this.chart = new Chart(this.chartRef.nativeElement, {
      type: 'bar' as ChartType,
      data: {
        labels: this.displayedData.map(d => d.name),
        datasets: [
          {
            label: 'Department Strength',
            data: this.displayedData.map(d => d.strength),
            backgroundColor: 'rgba(7, 218, 218)',
            barThickness: 15,  // Adjust bar thickness
            maxBarThickness: 30 // Maximum bar thickness
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // Keep aspect ratio similar to `depChartOptions`
        indexAxis: 'x', // Vertical bars
        plugins: {
          legend: { display: false }, // Hide legend
          datalabels: {
            anchor: 'end',
            align: 'end',
            font: { weight: 'bold', size: 12 },
            formatter: (value: number) => value
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { display: false },
            ticks: { font: { size: 8 } }
          },
          y: {
            beginAtZero: true,
            grid: { display: false },
            ticks: { font: { size: 7 } }
          }
        }
      }
    });
  }

  nextSlide(): void {
    if (this.currentPage < this.totalPages - 1) {
      this.currentPage++;
    } else {
      this.currentPage = 0;
    }
    this.updateChart();
  }

  previousSlide(): void {
    if (this.currentPage > 0) {
      this.currentPage--;
    } else {
      this.currentPage = this.totalPages - 1;
    }
    this.updateChart();
  }

  startAutoSlide(): void {
    this.autoSlideInterval = setInterval(() => {
      this.nextSlide();
    }, 5000);
  }

  stopAutoSlide(): void {
    if (this.autoSlideInterval) {
      clearInterval(this.autoSlideInterval);
    }
  }

  ngOnDestroy(): void {
    this.stopAutoSlide();
    if (this.timeInterval) {
      clearInterval(this.timeInterval); // Clear interval to prevent memory leaks
    }
  }



  categories = [
    { name: 'EMPLOYEE', color: '#D9534F', count: 0, icon: 'pi pi-users' },
    { name: 'CONTRACTOR', color: '#5CB85C', count: 0, icon: 'pi pi-briefcase' },
    { name: 'TEMPORARY', color: '#185c7e', count: 0, icon: 'pi pi-clock' },
    { name: 'TRAINEE', color: '#8A7F3D', count: 0, icon: 'pi pi-graduation-cap' },
    { name: 'Probationary', color: '#007bff', count: 0, icon: 'pi pi-user-plus' },
    { name: 'VENDOR', color: '#9B59B6', count: 0, icon: 'pi pi-truck' },
    { name: 'VISITORS', color: '#F39C12', count: 0, icon: 'pi pi-id-card' },
    { name: 'AMC', color: '#2C3E50', count: 0, icon: 'pi pi-wrench' },
    { name: 'GLOBAL', color: '#B2B2B2', count: 0, icon: 'pi pi-globe' },
    { name: 'HEAD OFFICE', color: '#28a745', count: 0, icon: 'pi pi-building' }
];

vehicleData = [
  { icon: 'fa', type: '2 Wheeler', totalSlots: 100, filledSlots: 0 },
  { icon: 'pi pi-car', type: '4 Wheeler', totalSlots: 50, filledSlots: 0 }
];


  employees = [
    { employeeId: 'EMP001', fullName: 'John Doe', gender: 'Male', age: 35, employeeType: 'Manager', department: 'R&D', workPermit: 'R&D', employmentStatus: 'Employee', civilStatus: 'Single', others: 'Vendor', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP002', fullName: 'Jane Smith', gender: 'Female', age: 28, employeeType: 'Staff', department: 'HR', workPermit: 'HR', employmentStatus: 'Contractor', civilStatus: 'Married', others: 'Visitor', vehicleType: '2-Wheeler' },
    { employeeId: 'EMP003', fullName: 'Michael Johnson', gender: 'Male', age: 32, employeeType: 'Operation', department: 'IT', workPermit: 'IT', employmentStatus: 'Temporary', civilStatus: 'Single', others: 'Visitor', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP004', fullName: 'Emily Davis', gender: 'Female', age: 64, employeeType: 'Manager', department: 'Marketing', workPermit: 'Marketing', employmentStatus: 'Trainee', civilStatus: 'Married', others: 'Vendor', vehicleType: '2-Wheeler' },
    { employeeId: 'EMP005', fullName: 'David Wilson', gender: 'Male', age: 46, employeeType: 'Staff', department: 'Sales', workPermit: 'Sales', employmentStatus: 'Probationary', civilStatus: 'Single', others: 'AMC', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP006', fullName: 'Chris Brown', gender: 'Male', age: 40, employeeType: 'Staff', department: 'Finance', workPermit: 'Finance', employmentStatus: 'Contractor', civilStatus: 'Married', others: 'Vendor', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP007', fullName: 'Laura White', gender: 'Female', age: 29, employeeType: 'Staff', department: 'People Operations', workPermit: 'People Operations', employmentStatus: 'Probationary', civilStatus: 'Single', others: 'Visitor', vehicleType: '2-Wheeler' },
    { employeeId: 'EMP008', fullName: 'James Miller', gender: 'Male', age: 57, employeeType: 'Manager', department: 'Legal', workPermit: 'Legal', employmentStatus: 'Contractor', civilStatus: 'Married', others: 'AMC', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP009', fullName: 'Sophia Green', gender: 'Female', age: 34, employeeType: 'Manager', department: 'Customer Support', workPermit: 'Customer Support', employmentStatus: 'Probationary', civilStatus: 'Single', others: 'Vendor', vehicleType: '2-Wheeler' },
    { employeeId: 'EMP010', fullName: 'Daniel Lee', gender: 'Male', age: 42, employeeType: 'Operation', department: 'Customer Management', workPermit: 'Customer Management', employmentStatus: 'Contractor', civilStatus: 'Married', others: 'Visitor', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP011', fullName: 'Olivia Taylor', gender: 'Female', age: 39, employeeType: 'Manager', department: 'Product', workPermit: 'Product', employmentStatus: 'Employee', civilStatus: 'Married', others: 'Global', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP012', fullName: 'Liam Harris', gender: 'Male', age: 45, employeeType: 'Staff', department: 'Others', workPermit: 'Others', employmentStatus: 'Employee', civilStatus: 'Single', others: 'Head Office', vehicleType: '2-Wheeler' },
    { employeeId: 'EMP013', fullName: 'Emma Roberts', gender: 'Female', age: 30, employeeType: 'Staff', department: 'Finance', workPermit: 'Finance', employmentStatus: 'Contractor', civilStatus: 'Single', others: 'Global', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP014', fullName: 'Noah Walker', gender: 'Male', age: 55, employeeType: 'Manager', department: 'Engineering', workPermit: 'Engineering', employmentStatus: 'Employee', civilStatus: 'Married', others: 'Head Office', vehicleType: '4-Wheeler' },
    { employeeId: 'EMP015', fullName: 'Ava King', gender: 'Female', age: 38, employeeType: 'Staff', department: 'Sales', workPermit: 'Sales', employmentStatus: 'Probationary', civilStatus: 'Single', others: 'Global', vehicleType: '2-Wheeler' }
];

  genderChartData: any;
  vehicleChartData: any;
  employeeTypeChartData: any;
  departmentChartData: any;
  workPermitChartData: any;
  employmentStatusChartData: any;
  othersChartData: any;
  civilStatusChartData: any;
  ageChartData: any;

  genderCounts: { [key: string]: number } = {};
  vehicleCounts: { [key: string]: number } = {};

  totalFilledSlots(): number {
    return this.vehicleData.reduce((sum, vehicle) => sum + vehicle.filledSlots, 0);
  }

  donutChartOptions: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'left',
      },
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
  plugins = [
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
        ctx.fillText(sum.toString(), width / 1.353, height / 2);
        ctx.save();
      },
    },
  ];




  chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'x',
    plugins: {
      legend: { display: false },
      datalabels: {
        display: true, // Ensure labels are displayed
        anchor: 'end', // Position label at the end of the bar
        align: 'top', // Place labels above bars
        font: { weight: 'bold', size: 14 },
        color: 'black',
        formatter: (value: number) => value > 0 ? value : '' // Hide zero values
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 10 } }
      },
      y: {
        grid: { display: false },
        beginAtZero: true,
        ticks: { font: { size: 12 } },
      }
    },
    elements: {
      bar: {
        borderWidth: 1,
        barPercentage: 0.7,
        categoryPercentage: 0.8
      }
    }
  };

  perChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    indexAxis: 'x', // Change to 'x' for vertical bars
    plugins: {
      legend: { display: false },
      datalabels: {
        anchor: 'end',
        align: 'end',
        font: { weight: 'bold', size: 12 },
        formatter: (value: number) => value
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: { display: false },
        ticks: { font: { size: 8 } }
      },
      y: {
        beginAtZero: true,
        grid: { display: false },
        ticks: { font: { size: 7 } }
      }
    },
    datasets: {
      bar: {
        barThickness: 10,
        maxBarThickness: 30,
      }
    }
  };

  vChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y', // Change to 'x' for vertical bars
    plugins: {
      legend: { display: false },
      datalabels: {
        anchor: 'end',
        align: 'right',
        color: 'bla',
        font: { weight: 'bold', size: 12 },
        formatter: (value: number) => value
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: { display: false },
        ticks: { font: { size: 10 } }
      },
      y: {
        grid: { display: false },
        ticks: { font: { size: 10 } }
      }
    }
  };


  ngOnInit() {
    this.updateVehicleSlots();
    this.calculateDepartmentStrength();
    this.startAutoSlide();
    this.prepareChartData();
    this.prepareDonutChartData()
    this.civilChartData();
    this.genderCounts = this.countGender();
    this.vehicleCounts = this.countVehicleType();

    this.updateTime();

    this.timeInterval = setInterval(() => {
      this.updateTime();
      this.cdr.detectChanges(); // Detect changes without reloading the entire component
    }, 1000);
  }


  countCivilStatus(): { [key: string]: number } {
    return this.employees.reduce((acc, emp) => {
      acc[emp.civilStatus] = (acc[emp.civilStatus] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });
  }

  civilChartData() {
    const data = this.countCivilStatus();
    this.civilStatusChartData = {
      labels: Object.keys(data),
      datasets: [
        {
          data: Object.values(data),
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
          hoverBackgroundColor: ['#d9534f', '#5cb85c', '#f0ad4e', '#5bc0de'],
        },
      ],
    };
  }


  countAgeGroups(): { [key: string]: number } {
    const ageGroups = {
      '21-30': 0,
      '31-40': 0,
      '41-50': 0,
      '51-60': 0,
      '61-70': 0
    };

    this.employees.forEach(emp => {
      if (emp.age >= 21 && emp.age <= 30) ageGroups['21-30']++;
      else if (emp.age >= 31 && emp.age <= 40) ageGroups['31-40']++;
      else if (emp.age >= 41 && emp.age <= 50) ageGroups['41-50']++;
      else if (emp.age >= 51 && emp.age <= 60) ageGroups['51-60']++;
      else if (emp.age >= 61 && emp.age <= 70) ageGroups['61-70']++;
    });

    return ageGroups;
  }


countGender(): { [key: string]: number } {
    return {
        Male: this.employees.filter(emp => emp.gender === 'Male').length,
        Female: this.employees.filter(emp => emp.gender === 'Female').length
    };
}

countVehicleType(): { [key: string]: number } {
    return {
        '2-Wheeler': this.employees.filter(emp => emp.vehicleType === '2-Wheeler').length,
        '4-Wheeler': this.employees.filter(emp => emp.vehicleType === '4-Wheeler').length
    };
}

updateVehicleSlots() {
  const vehicleCounts = this.countVehicleType();

  this.vehicleData.forEach(vehicle => {
      const typeKey = vehicle.type.replace(' ', '-'); // Convert "2 Wheeler" to "2-Wheeler" to match keys
      vehicle.filledSlots = vehicleCounts[typeKey] || 0; // Update filledSlots with actual count
  });
}

countEmployeeType(): { [key: string]: number } {
  return this.employees.reduce((acc, emp) => {
    acc[emp.employeeType] = (acc[emp.employeeType] || 0) + 1;
    return acc;
  }, {} as { [key: string]: number });
}

countDepartment(): { [key: string]: number } {
    const departments = [...new Set(this.employees.map(emp => emp.department))];
    let counts: { [key: string]: number } = {};
    departments.forEach(dept => {
        counts[dept] = this.employees.filter(emp => emp.department === dept).length;
    });
    return counts;
}

countWorkPermit(): { [key: string]: number } {
    const workPermits = [...new Set(this.employees.map(emp => emp.workPermit))];
    let counts: { [key: string]: number } = {};
    workPermits.forEach(permit => {
        counts[permit] = this.employees.filter(emp => emp.workPermit === permit).length;
    });
    return counts;
}

countEmploymentStatus(): { [key: string]: number } {
    const statuses = [...new Set(this.employees.map(emp => emp.employmentStatus))];
    let counts: { [key: string]: number } = {};
    statuses.forEach(status => {
        counts[status] = this.employees.filter(emp => emp.employmentStatus === status).length;
    });
    return counts;
}

countOthers(): { [key: string]: number } {
    const othersCategories = [...new Set(this.employees.map(emp => emp.others))];
    let counts: { [key: string]: number } = {};
    othersCategories.forEach(category => {
        counts[category] = this.employees.filter(emp => emp.others === category).length;
    });
    return counts;
}


prepareChartData() {
  this.departmentChartData = this.createBarChart(this.countDepartment(), '#42A5F5');
  this.workPermitChartData = this.createBarChart(this.countWorkPermit(), '#66BB6A');
  this.employmentStatusChartData = this.createBarChart(this.countEmploymentStatus(), '#FFA726');
  this.othersChartData = this.createBarChart(this.countOthers(), '#AB47BC');
  this.ageChartData = this.createBarChart(this.countAgeGroups(), '#FF5733');
}

prepareDonutChartData() {
  const data = this.countEmployeeType();
  this.employeeTypeChartData = {
    labels: Object.keys(data),
    datasets: [
      {
        data: Object.values(data),
        backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4BC0C0', '#9966FF'],
        hoverBackgroundColor: ['#d9534f', '#5cb85c', '#f0ad4e', '#5bc0de', '#6f42c1'],
      },
    ],
  };
}

  createPieChart(data: { [key: string]: number }, colors: string[]) {
    return {
      labels: Object.keys(data),
      datasets: [{ data: Object.values(data), backgroundColor: colors }]
    };
  }

  createBarChart(data: { [key: string]: number }, color: string) {
    return {
      labels: Object.keys(data),
      datasets: [{ backgroundColor: color, data: Object.values(data) }]
    };
  }

}
