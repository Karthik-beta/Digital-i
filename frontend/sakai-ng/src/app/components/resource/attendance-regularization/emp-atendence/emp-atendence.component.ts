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

@Component({
  selector: 'app-emp-atendence',
  templateUrl: './emp-atendence.component.html',
  styleUrl: './emp-atendence.component.scss'
})
export class EmpAtendenceComponent {
    allSelected: boolean = false;
    indeterminate: boolean = false;
    shift: boolean = false;
    WO: boolean = false;

    test = [
        { employee_id: 'A10195', employee_name: 'John Doe', selected: false },
        { employee_id: 'A10291', employee_name: 'Jane Smith', selected: false }
    ];

    toggleAllSelection() {
        // Toggle all rows based on the header checkbox state
        this.test.forEach(item => (item.selected = this.allSelected));
        this.indeterminate = false; // Reset indeterminate state
    }

    checkIfAllSelected() {
        const selectedCount = this.test.filter(item => item.selected).length;

        // Update the `allSelected` and `indeterminate` states
        this.allSelected = selectedCount === this.test.length;
        this.indeterminate = selectedCount > 0 && selectedCount < this.test.length;
    }

  dateRange: [Date, Date] | null = [
    new Date(),
    new Date(new Date().setDate(new Date().getDate() + 7)) // Default 7-day range
  ];

  employees = [
    { id: 'A10195', name: 'GANDLE ADITYA VISHWJEET' },
    { id: 'A10291', name: 'Dete Rakesh Ramkrushna' }
  ];

  filteredEmployees = [...this.employees];
  searchTerm = '';

  daysInRange: Date[] = [];
  shiftOptions = ['GS','FS', 'SS', 'NS', 'WO'];
  scheduleData: { [empId: string]: { [date: string]: string } } = {};

  selectedLabel = 'Export';
  selectedIcon = 'pi pi-upload';

  items = [
    {
      label: 'Excel',
      icon: 'pi pi-file-excel',
      command: () => {
        this.selectedLabel = 'Excel';
        this.selectedIcon = 'pi pi-file-excel';
        this.exportToExcel();
      }
    },
    {
      label: 'PDF',
      icon: 'pi pi-file-pdf',
      command: () => {
        this.selectedLabel = 'PDF';
        this.selectedIcon = 'pi pi-file-pdf';
        this.exportToPDF();
      }
    }
  ];

  ngOnInit() {
    this.generateDaysInRange();
    this.initializeScheduleData();
  }

  filterEmployees() {
    if (!this.searchTerm) {
      this.filteredEmployees = [...this.employees];
      return;
    }
    this.filteredEmployees = this.employees.filter(emp =>
      emp.id.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  generateDaysInRange() {
    this.daysInRange = [];
    if (!this.dateRange?.[0] || !this.dateRange?.[1]) return;

    const start = new Date(this.dateRange[0]);
    const end = new Date(this.dateRange[1]);
    const current = new Date(start);

    while (current <= end) {
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

  onDateRangeChange() {
    this.generateDaysInRange();
    this.initializeScheduleData();
  }

  private formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
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

  onMonthChange() {
    this.generateDays();
    this.initializeScheduleData();
  }

  getShiftValue(employeeId: string, day: Date): string {
    const dateStr = this.formatDate(day);
    return this.scheduleData[employeeId]?.[dateStr] || '-';
  }

  onShiftChange(employeeId: string, day: Date, value: string) {
    const dateStr = this.formatDate(day);
    if (!this.scheduleData[employeeId]) {
      this.scheduleData[employeeId] = {};
    }
    this.scheduleData[employeeId][dateStr] = value;
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
    // Implement your date formatting logic here
    // For simplicity, using ISO string in this example
    return date.toISOString().split('T')[0];
  }

}
