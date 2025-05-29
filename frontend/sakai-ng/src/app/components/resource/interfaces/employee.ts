export interface Stat {
    title: string;
    value: number;
    icon: string;
    color: string;
  }
  
  export interface ChartData {
    labels: string[];
    datasets: { label: string; backgroundColor: string; borderColor: string; data: number[] }[];
  }
  
  export interface ChartOptions {
    responsive: boolean;
    maintainAspectRatio: boolean;
    scales: { y: { beginAtZero: boolean; max: number } };
  }
  
  export interface StatusSummary {
    count: number;
    label: string;
    icon: string;
    color: string;
  }
  
  
  export interface Employee {
    name: string;
    empId: number;
    image: string;
    leaveType: string;
  }

  