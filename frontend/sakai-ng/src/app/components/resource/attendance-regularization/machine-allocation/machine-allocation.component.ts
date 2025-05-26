import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CalendarModule } from 'primeng/calendar';
import { DropdownModule } from 'primeng/dropdown';
import { SplitButtonModule } from 'primeng/splitbutton';
import { TableModule } from 'primeng/table';

import * as XLSX from 'xlsx';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

import { MachineService } from './machine-allocation.service';
import { HttpClientModule } from '@angular/common/http';
import { CheckboxModule } from 'primeng/checkbox';

interface Shopfloor {
  id: number;
  shopfloor_name: string;
}

interface Machine {
  id: number;
  shopfloor_id: number;
  machine_name: string;
  machine_id: string;
}

@Component({
  selector: 'app-machine-allocation',
  standalone: true,
  imports : [CommonModule,FormsModule, CheckboxModule, HttpClientModule, CalendarModule, TableModule, DropdownModule, SplitButtonModule],
  templateUrl: './machine-allocation.component.html',
  styleUrl: './machine-allocation.component.scss'
})
export class MachineAllocationComponent {
  dateRange: [Date, Date] | null = [
    new Date(),
    new Date() // Default 7-day range
  ];

  showTransactions: boolean = false;
  machines: any[] = [];
  machineDateRows: any[] = [];
  shopfloors: any[] = [];
  loading: boolean = true;
  errorMessage: string;

  constructor(private machineService: MachineService) {}

  employees = [
    { id: 'A10195', name: 'GANDLE ADITYA VISHWJEET' },
    { id: 'A10291', name: 'Dete Rakesh Ramkrushna' },
    { id: 'A10345', name: 'Patil Sachin Sunil' },
    { id: 'A10422', name: 'Sharma Ravi Kumar' },
    { id: 'A10567', name: 'Verma Priya Singh' },
    { id: 'A10689', name: 'Reddy Anil Kumar' },
  ];

  skillMatrices = [
    // { id: 'SM001', name: 'CNC Machining' },
    // { id: 'SM002', name: 'Welding' },
    // { id: 'SM003', name: 'Quality Inspection' },
    // { id: 'SM004', name: 'Preventive Maintenance' },
    // { id: 'SM005', name: 'PLC Programming' },
    // { id: 'SM006', name: 'Painting' },
    // { id: 'SM007', name: 'Packaging' },
  ];

  private shiftShortNames = [
    { id: 1, shortName: 'GS' },
    { id: 2, shortName: 'FS' },
    { id: 3, shortName: 'SS' },
    { id: 4, shortName: 'NS' },
    { id: 5, shortName: 'WO' }
  ];

  // shopfloors: Shopfloor[] = [
  //   { id: 1, shopfloor_name: 'SHOP -1' },
  //   { id: 2, shopfloor_name: 'SHOP -2' },
  //   { id: 3, shopfloor_name: 'SHOP -3' }
  // ];
  
  // machines: Machine[] = [
  //   { id: 1, shopfloor_id: 1, machine_name: 'TURNMASTER-50-1', machine_id: 'TM50-1' },
  //   { id: 2, shopfloor_id: 1, machine_name: 'HMT - Praga Precision Surface Grinding', machine_id: 'HMT-PPSG' },
  //   { id: 3, shopfloor_id: 1, machine_name: 'Vertical Milling Machine', machine_id: 'VMM-1' },
  //   { id: 4, shopfloor_id: 1, machine_name: 'THREAD ROLLING 514', machine_id: 'TR-514' },
  //   { id: 5, shopfloor_id: 1, machine_name: 'THREAD ROLLING HMT 514', machine_id: 'TR-HMT-514' },
  //   { id: 6, shopfloor_id: 1, machine_name: 'BATLIBOI RADIAL DRILLING', machine_id: 'BRD-1' },
  //   { id: 7, shopfloor_id: 1, machine_name: 'GODREJ 25 T PRESS', machine_id: 'G25T' },
  //   { id: 8, shopfloor_id: 1, machine_name: 'GODREJ 40 T PRESS', machine_id: 'G40T' },
  //   { id: 9, shopfloor_id: 1, machine_name: 'GODREJ 63 T PRESS', machine_id: 'G63T' },
  //   { id: 10, shopfloor_id: 1, machine_name: 'GODREJ 100 T PRESS', machine_id: 'G100T' },
  //   { id: 11, shopfloor_id: 1, machine_name: '100T MANKOO PRESS', machine_id: 'MK100T-1' },
  //   { id: 12, shopfloor_id: 1, machine_name: '100T MANKOO PRESS', machine_id: 'MK100T-2' },
  //   { id: 13, shopfloor_id: 1, machine_name: '200 T MANKOO PRESS', machine_id: 'MK200T' },
  
  //   { id: 14, shopfloor_id: 2, machine_name: 'FRONIOUS TPS MIG WELDING MACHINE:4000', machine_id: 'FTPS-4000-1' },
  //   { id: 15, shopfloor_id: 2, machine_name: 'FRONIOUS TPS MIG WELDING MACHINE:4000', machine_id: 'FTPS-4000-2' },
  //   { id: 16, shopfloor_id: 2, machine_name: 'FRONIOUS TPS MIG WELDING MACHINE:4000', machine_id: 'FTPS-4000-3' },
  //   { id: 17, shopfloor_id: 2, machine_name: 'FRONIOUS TPS MIG WELDING MACHINE:4000', machine_id: 'FTPS-4000-4' },
  //   { id: 18, shopfloor_id: 2, machine_name: 'FRONIOUS TPS MIG WELDING MACHINE:4000', machine_id: 'FTPS-4000-5' },
  //   { id: 19, shopfloor_id: 2, machine_name: 'LAXON BANDSAW MACHINE', machine_id: 'LBM-1' },
  //   { id: 20, shopfloor_id: 2, machine_name: 'THREAD ROLLING ORT', machine_id: 'TR-ORT' },
  //   { id: 21, shopfloor_id: 2, machine_name: 'SPM DRILLING', machine_id: 'SPM-DRILL' },
  //   { id: 22, shopfloor_id: 2, machine_name: 'Mechanical Power Press - 45T', machine_id: 'MPP-45T' },
  //   { id: 23, shopfloor_id: 2, machine_name: 'LAXON BANDSAW MACHINE / CIRCULAR SAW', machine_id: 'LBM-CS' },
  //   { id: 24, shopfloor_id: 2, machine_name: 'PAINTSHOP OPERATION', machine_id: 'PS-OP' },
  //   { id: 25, shopfloor_id: 2, machine_name: 'LINE 11', machine_id: 'LINE-11' },
  //   { id: 26, shopfloor_id: 2, machine_name: 'LINE 3', machine_id: 'LINE-3' },
  //   { id: 27, shopfloor_id: 2, machine_name: 'LINE 4', machine_id: 'LINE-4' },
  
  //   { id: 28, shopfloor_id: 3, machine_name: 'Mankoo Power Press with Pneumatic Clutch - 100T', machine_id: 'MKPP-100T' },
  //   { id: 29, shopfloor_id: 3, machine_name: 'Mechanical Power Press - 110T', machine_id: 'MPP-110T-1' },
  //   { id: 30, shopfloor_id: 3, machine_name: 'Mechanical Power Press - 110T', machine_id: 'MPP-110T-2' },
  //   { id: 31, shopfloor_id: 3, machine_name: 'Mechanical Power Press - 45T', machine_id: 'MPP-45T-S3' },
  //   { id: 32, shopfloor_id: 3, machine_name: 'LAXON BANDSAW MACHINE', machine_id: 'LBM-S3' },
  //   { id: 33, shopfloor_id: 3, machine_name: 'Power Press Pneumatic Clutch Operated - 100T Mankoo Make', machine_id: 'MKPP-100T-PC' },
  //   { id: 34, shopfloor_id: 3, machine_name: 'AMC-PBSC-16', machine_id: 'AMC-PBSC-16-1' },
  //   { id: 35, shopfloor_id: 3, machine_name: 'AMC-PBSC-16', machine_id: 'AMC-PBSC-16-2' },
  //   { id: 36, shopfloor_id: 3, machine_name: 'SEC. STRAIGHTENING', machine_id: 'SEC-STR' },
  //   { id: 37, shopfloor_id: 3, machine_name: 'PORTABLE PROFILE CUTTING MACHINE', machine_id: 'PPCM' },
  //   { id: 38, shopfloor_id: 3, machine_name: 'HMT RADIAL DRILLING', machine_id: 'HMT-RD' },
  //   { id: 39, shopfloor_id: 3, machine_name: 'BAR BENDING ICARO-1', machine_id: 'BB-ICARO1' },
  //   { id: 40, shopfloor_id: 3, machine_name: 'LINE 1 (JACK SPINDLE)', machine_id: 'LINE1-JS' },
  //   { id: 41, shopfloor_id: 3, machine_name: 'LINE 1 (J70)', machine_id: 'LINE1-J70' }
  // ];
  
  // Sample transaction data array (5 entries)
  transactionsList = [];

  filteredMachines = [...this.machines];
  searchTerm = '';

  // daysInRange: Date[] = [];

  daysInRange: Date[] = [new Date(), new Date()];

  shiftOptions = [ ];
  
  scheduleData: { [empId: string]: { [date: string]: string } } = {};
  employeeData: { [machineId: string]: { [operatorId: string]: string } } = {};

  selectedMachines: { [key: string]: boolean } = {};
  selectAll: boolean = false;

  operatorList: { id: number; name: string }[] = [
    { id: 1, name: 'Operator 1' },
    { id: 2, name: 'Operator 2' },
    { id: 3, name: 'Operator 3' },
    { id: 4, name: 'Operator 4' },
    { id: 5, name: 'Operator 5' }
  ];

  selectedExportLabel = 'Export';
  selectedExportIcon = 'pi pi-upload';
  selectedImportLabel = 'Import';
  selectedImportIcon = 'pi pi-download';

  importItems = [
    {
        label: 'Import Excel',
        icon: 'pi pi-file-excel',
        command: () =>{
          this.selectedImportLabel = 'Excel';
          this.selectedImportIcon = 'pi pi-file-excel';
          this.importExcel()
        } 
    },
    {
        label: 'Import CSV',
        icon: 'pi pi-file',
        command: () => {
          this.selectedImportLabel = 'CSV';
          this.selectedImportIcon = 'pi pi-file';
          this.importCSV()
        } 
    }
  ];
  
  items = [
    {
      label: 'Excel',
      icon: 'pi pi-file-excel',
      command: () => {
        this.selectedExportLabel = 'Excel';
        this.selectedExportIcon = 'pi pi-file-excel';
        this.exportToExcel();
      }
    },
    {
      label: 'PDF',
      icon: 'pi pi-file-pdf',
      command: () => {
        this.selectedExportLabel = 'PDF';
        this.selectedExportIcon = 'pi pi-file-pdf';
        this.exportToPDF();
      }
    }
  ];

  
  selectedShift: string; 

  // transactionsList: any[] = []; // Array to store saved transactions
  lastTransactionId = 0; 

  getShiftIdByShortName(sname : any) {
    const shiftIds = {
      'GS': 1,
      'FS': 2,
      'SS': 3,
      'NS': 4,
      'WF': 5
    };
    
    return shiftIds[sname.toUpperCase()] || null; // Returns null if not found
  }
  saveTransactions() {
    if (!this.dateRange) {
      alert('Please select a date range first');
      return;
    }

    // Get selected machines
    const selectedMachines = this.MachinesWithDates.filter(
      machine => this.selectedMachines[machine.id]
    );

    if (selectedMachines.length === 0) {
      alert('Please select at least one machine');
      return;
    }

    // Process each selected machine
    selectedMachines.forEach(machine => {
      const transactionId = this.generateTransactionId(machine.id, machine.displayDate);
      
      // Increment ID counter
      this.lastTransactionId += 1;

      const formattedDate = this.formatDateToYMD(machine.displayDate);

      // Create transaction object with integer ID
      const newTransaction = {
        id: this.lastTransactionId,
        transaction_id: `TRANS${this.lastTransactionId.toString().padStart(3, '0')}`,
        date: formattedDate,
        machine: machine.id,
        shopfloor: machine.shopfloor,
        shift_timing: this.getShiftIdByShortName(machine.shift) || null,
        skill_matrix: machine.skill,  // Add the selected skill ID here
        operator_1: this.getEmpValue(machine.id.toString(), '1')?.id || null,
        operator_2: this.getEmpValue(machine.id.toString(), '2')?.id || null,
        operator_3: this.getEmpValue(machine.id.toString(), '3')?.id || null,
        operator_4: this.getEmpValue(machine.id.toString(), '4')?.id || null,
        operator_5: this.getEmpValue(machine.id.toString(), '5')?.id || null
      };
      this.machineService.createMachineTransaction(newTransaction).subscribe({
        next: (createdTransaction) => {
          console.log('Transaction created:', createdTransaction);
          this.transactionsList = [...this.transactionsList, createdTransaction];
        },
        error: (err) => {
          console.error('Error creating transaction:', err);
          alert('Error creating transaction:');
        }
      });
      this.transactionsList.push(newTransaction);
    });

    console.log('Saved transactions:', this.transactionsList);
    alert(`${selectedMachines.length} transaction(s) saved successfully!`);
  }

  private formatDateToYMD(dateStr: string): string {
    const [day, month, year] = dateStr.split('/');
    const fullYear = year.length === 2 ? `20${year}` : year;
    return `${fullYear}-${month}-${day}`;
  }

  private generateTransactionId(machineId: number, dateStr: string): string {
    const datePart = dateStr.replace(/\//g, '');
    return `TRX-${machineId}-${datePart}`;
  }
  applyShiftToSelectedMachines(shiftId: String) {
    // Check if there are any selected machines by checking the object keys
    if (Object.keys(this.selectedMachines).length > 0) {
      for (const machine of this.MachinesWithDates) {
        if (this.selectedMachines[machine.id]) {
            machine.shift = shiftId;
        }
      }
      return;
    } else {
      alert('Please select at least one machine');
      return;
    }
}
    ngOnInit() {
    
    this.generateDaysInRange();
    
    this.initializeScheduleData();
    
    this.fetchMachines();
    this.fetchShopfloors();
    this.fetchShifts();
    this.fetchSkillMatrices();
    
    this.generateMachineDateRows();
    
    this.onDateRangeChange();
  }

  fetchMachines(): void {
    this.loading = true;
    this.machineService.getMachines().subscribe({
      next: (data) => {
        this.machines = data;
        this.filteredMachines = [...this.machines]; 
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching machines:', err);
        this.loading = false;
        this.errorMessage = 'Failed to load machines. Please try again later.';
      }
    });
  }

  fetchShopfloors(): void {
    this.loading = true;
    this.machineService.getShopfloors().subscribe({
      next: (data) => {
        this.shopfloors = data;
        this.shopfloors = [...this.shopfloors]; // Update filtered list if needed
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching shopfloors:', err);
        this.loading = false;
        this.errorMessage = 'Failed to load shopfloors. Please try again later.';
      }
    });
  }


  fetchShifts(): void {
    this.loading = true;
    this.machineService.getShifts().subscribe({
      next: (data) => {
        this.shiftOptions = data.map((shift: { id: number; }) => {
          const shortName = this.shiftShortNames.find(s => s.id === shift.id)?.shortName || 'NA';
          return {
            ...shift,
            sname: shortName // Replace name with shortName
          };
        });
        
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching shifts:', err);
        this.loading = false;
        this.errorMessage = 'Failed to load shifts. Please try again later.';
      }
    });
  }

  fetchSkillMatrices(): void {
    this.loading = true;
    this.machineService.getSkillMatrixs().subscribe({
      next: (data: any) => {
        this.skillMatrices = data;
        this.skillMatrices = [...this.skillMatrices];
        console.log(this.skillMatrices)
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching skill matrices:', err);
        this.loading = false;
        this.errorMessage = 'Failed to load skill matrices. Please try again later.';
      }
    });
  }

  onTransactionsClick() {
    this.showTransactions = true;  // Switch to transactions view
    
    // Only fetch if data hasn't been loaded yet (or force refresh if needed)
    // if (!this.transactionsList || this.transactionsList.length === 0) {
      this.fetchMachineTransactions();
    // }
  }

fetchMachineTransactions(): void {
  this.loading = true;
  this.machineService.getMachineTransactions().subscribe({
    next: (data) => {
      this.transactionsList = data;
      this.transactionsList = [...this.transactionsList]; // Create new reference for change detection
      this.loading = false;
    },
    error: (err) => {
      console.error('Error fetching machine transactions:', err);
      this.loading = false;
      this.errorMessage = 'Failed to load machine transactions. Please try again later.';
    }
  });
}

generateMachineDateRows() {
  this.machineDateRows = [];

  if (!this.dateRange || !this.dateRange[0] || !this.dateRange[1]) return;

  const [startDate, endDate] = this.dateRange;
  const dateList = this.getDateListBetween(startDate, endDate);

  for (const machine of this.filteredMachines) {
    for (const date of dateList) {
      this.machineDateRows.push({
        ...machine,
        displayDate: this.formatDate(date),
        rawDate: date
      });
    }
  }
}

  getDateListBetween(start: Date, end: Date): Date[] {
    const dates: Date[] = [];
    let current = new Date(start);

    while (current <= end) {
      dates.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }

    return dates;
  }


  filterMachines() {
    if (!this.searchTerm) {
      this.filteredMachines = [...this.machines];
    } else {
      this.filteredMachines = this.machines.filter(machine => 
        machine.machine_name.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
    
    this.onDateRangeChange();
  }

  generateDaysInRange(startDate: Date = new Date()) {
  this.daysInRange = [];

  const numberOfDays = this.operatorList.length;
  const current = new Date(startDate);

  for (let i = 0; i < numberOfDays; i++) {
    this.daysInRange.push(new Date(current));
    current.setDate(current.getDate() + 1);
  }
}


  initializeScheduleData() {
    this.employees.forEach(emp => {
      if (!this.scheduleData[emp.id]) {
        this.scheduleData[emp.id] = {};
      }
      this.daysInRange.forEach(date => {
        const dateStr = this.formatDate(date);
        if (!this.scheduleData[emp.id][dateStr]) {
          this.scheduleData[emp.id][dateStr] = '-';
        }
      });
    });
  }

  
  MachinesWithDates: any[] = [];
  onDateRangeChange() {
    this.MachinesWithDates = [];
    
    if (this.dateRange && this.dateRange[0] && this.dateRange[1]) {
      // Clone dates to avoid reference issues
      const startDate = new Date(this.dateRange[0]);
      const endDate = new Date(this.dateRange[1]);
      
      // Reset time part to avoid timezone issues
      startDate.setHours(0, 0, 0, 0);
      endDate.setHours(0, 0, 0, 0);
      
      // Generate dates in range
      const dates = this.getDatesInRange(startDate, endDate);
      
      // Create machine entries for each date
      dates.forEach(date => {
        this.filteredMachines.forEach(machine => {
          this.MachinesWithDates.push({
            ...machine,
            displayDate: this.formatDate(date),
            originalDate: new Date(date)  // Store date object for reference
          });
        });
      });
    }
  }
  
  // Improved getDatesInRange function
  private getDatesInRange(startDate: Date, endDate: Date): Date[] {
    const dates = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      dates.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return dates;
  }
  

  private formatDate(date: Date): string {
    const d = new Date(date);
    const day = d.getDate().toString().padStart(2, '0');
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const year = d.getFullYear().toString().slice(-2);
    return `${day}/${month}/${year}`;
  }

  generateDays() {
    // Clear previous days
    this.daysInRange = [];
    
    // Check if date range is valid
    if (!this.dateRange || !this.dateRange[0] || !this.dateRange[1]) {
        return;
    }

    const startDate = new Date(this.dateRange[0]);
    const endDate = new Date(this.dateRange[1]);
    const currentDate = new Date(startDate);

    // Iterate through each day in the range
    while (currentDate <= endDate) {
        this.daysInRange.push(new Date(currentDate));
        currentDate.setDate(currentDate.getDate() + 1);
    }
  }


  toggleSelectAll() {
      if (this.selectAll) {
          this.filteredMachines.forEach(machine => {
              this.selectedMachines[machine.id] = true;
          });
      } else {
          this.selectedMachines = {};
      }
  }

  onMachineSelect(machineId: string) {
      // Check if all machines are selected
      const allSelected = this.filteredMachines.every(machine => this.selectedMachines[machine.id]);
      this.selectAll = allSelected;
  }

  // To get the list of selected machine IDs
  getSelectedMachineIds(): string[] {
      return Object.keys(this.selectedMachines).filter(id => this.selectedMachines[id]);
  }

  getShopfloorName(shopfloorId: number): string {
    const shopfloor = this.shopfloors.find(s => s.id === shopfloorId);
    return shopfloor ? shopfloor.shopfloor_name : 'Unknown';
  }

  getShopfloorIdByName(shopfloorName: string): number | null {
    const shopfloor = this.shopfloors.find(s => s.shopfloor_name === shopfloorName);
    return shopfloor ? shopfloor.id : null;
  }

  getShiftShortName(shiftId: number): string {
    const shift = this.shiftOptions.find(s => s.id === shiftId);
    return shift ? shift.sname : '-';
  }

  getMachineName(machineId: number): string {
    if (!this.machines) return machineId.toString();
    
    const machine = this.machines.find(m => m.id === machineId);
    return machine ? machine.machine_name : machineId.toString();
  }


  getShiftValue(machineId: string, day: Date): string {
    const dateStr = this.formatDate(day);
    return this.scheduleData[machineId]?.[dateStr] || '-';
  }
  
  onShiftChange(machineId: string, day: Date, value: string) {
    const dateStr = this.formatDate(day);
    if (!this.scheduleData[machineId]) {
      this.scheduleData[machineId] = {};
    }
    this.scheduleData[machineId][dateStr] = value;
  }


  getEmpValue(machineId: string, operatorId: string): any {
      const employeeId = this.employeeData[machineId]?.[operatorId];
      return this.employees.find(emp => emp.id === employeeId) || null;
  }

  onEmpChange(machineId: string, operatorId: string, employee: any) {
      if (!this.employeeData[machineId]) {
          this.employeeData[machineId] = {};
      }
      
      if (employee) {
          this.employeeData[machineId][operatorId] = employee.id; // Store just the ID
      } else {
          delete this.employeeData[machineId][operatorId];
          
          if (Object.keys(this.employeeData[machineId]).length === 0) {
              delete this.employeeData[machineId];
          }
      }
  }

  importExcel() {
      // Implement logic to open file dialog or process Excel import
      console.log('Import Excel clicked');
      // this.fileUpload.nativeElement.click(); (if using file input)
  }

  importCSV() {
      console.log('Import CSV clicked');
      // Logic to handle CSV
  }
  exportToExcel() {
    if (this.employees.length === 0) {
      console.warn('No employee data to export');
      return;
    }

    // Format data for Excel
    const formattedData = this.employees.map(employee => {
      const employeeData: any = {
        'Employee ID': employee.id,
        'Employee Name': employee.name
      };

      // Add each day's shift
      this.daysInRange.forEach(day => {
        const dateStr = this .formatDate(day);
        employeeData[dateStr] = this.scheduleData[employee.id]?.[dateStr] || '-';
      });

      return employeeData;
    });

    // Create worksheet
    const worksheet = XLSX.utils.json_to_sheet(formattedData);
    
    // Create workbook
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Employee Attendance');
    
    // Set column widths
    const wscols = [
      {wch: 15}, // Employee ID
      {wch: 25}, // Employee Name
      ...this.daysInRange.map(() => ({wch: 10})) // Each date column
    ];
    worksheet['!cols'] = wscols;
    
    // Generate Excel file with timestamp
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, '');
    XLSX.writeFile(workbook, `Employee_Attendance_${timestamp}.xlsx`);
  }

  exportToPDF() {
    if (this.employees.length === 0) {
      console.warn('No employee data to export');
      return;
    }

    try {
      // Create new PDF document (landscape to fit all columns)
      const doc = new jsPDF('l', 'mm', 'a4');

      // Add title
      doc.setFontSize(18);
      doc.setTextColor(40);
      doc.setFont('helvetica', 'bold');
      doc.text('Employee Attendance Report', 14, 20);

      // Add timestamp
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      const timestamp = new Date().toLocaleString();
      doc.text(`Generated on: ${timestamp}`, 14, 27);

      // Prepare headers
      const headers = [
        ['Employee ID', 'Employee Name', 
         ...this.daysInRange.map(day => this.changeDate(day, 'dd-MMM'))
        ]
      ];

      // Prepare data
      const data = this.employees.map(employee => {
        const row = [employee.id, employee.name];
        this.daysInRange.forEach(day => {
          const dateStr = this.formatDate(day);
          row.push(this.scheduleData[employee.id]?.[dateStr] || '-');
        });
        return row;
      });

      // Add table to PDF
      autoTable(doc, {
        head: headers,
        body: data,
        startY: 30,
        margin: { left: 14 },
        headStyles: {
          fillColor: [41, 128, 185],
          textColor: 255,
          fontStyle: 'bold',
          fontSize: 8
        },
        styles: {
          fontSize: 7,
          cellPadding: 2,
          overflow: 'linebreak',
          valign: 'middle'
        },
        columnStyles: {
          0: { cellWidth: 15 },  // Employee ID
          1: { cellWidth: 25 },  // Employee Name
          // Dynamic columns for dates
          ...Object.fromEntries(
            Array.from({length: this.daysInRange.length}, (_, i) => [i + 2, {cellWidth: 10}])
          )
        },
        didDrawPage: (data) => {
          // Footer
          doc.setFontSize(8);
          doc.setTextColor(100);
          const pageCount = doc.getNumberOfPages();
          doc.text(`Page ${data.pageNumber} of ${pageCount}`, data.settings.margin.left, doc.internal.pageSize.height - 10);
        }
      });

      // Save the PDF
      doc.save(`Employee_Attendance_${new Date().toISOString().slice(0, 10)}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please check console for details.');
    }
  }

  private changeDate(date: Date, format: string = 'yyyy-MM-dd'): string {
    return date.toISOString().split('T')[0];
  }

}
