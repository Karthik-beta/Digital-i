import { Component, OnInit } from '@angular/core';
import { SharedService } from 'src/app/shared.service';
import { MessageService, ConfirmationService, ConfirmEventType } from 'primeng/api';

@Component({
  selector: 'app-reset-report',
  templateUrl: './reset-report.component.html',
  styleUrl: './reset-report.component.scss'
})
export class ResetReportComponent implements OnInit{

    constructor(
        private service: SharedService,
        private messageService: MessageService,
        private confirmationService: ConfirmationService
    ) { }

    ngOnInit(): void {

    }

    resetReport() {
        this.confirmationService.confirm({
            message: 'Are you sure you want to reset all reports?',
            header: 'Reset All Reports',
            icon: 'pi pi-exclamation-triangle',
            acceptButtonStyleClass: "p-button-danger p-button-text",
            rejectButtonStyleClass: "p-button-text p-button-text",
            accept: () => {
                this.service.resetReports().subscribe({
                    next: (response) => {
                        this.messageService.add({ severity: 'success', summary: 'Success', detail: 'The request have been successfully registered. Please check back after 5 minutes.' });
                    },
                    error: (error) => {
                        this.messageService.add({ severity: 'warn', summary: 'Error', detail: 'An error occurred while attempting to register the request.' });
                    }
                });
            },
            reject: (type: any) => {
                switch (type) {
                    case ConfirmEventType.REJECT:
                        this.messageService.add({ severity: 'info', summary: 'Information', detail: 'The request operation has been rejected.' });
                        break;
                    case ConfirmEventType.CANCEL:
                        this.messageService.add({ severity: 'warn', summary: 'Warning', detail: 'The request operation has been canceled.' });
                        break;
                }
            }
        });
    }

}
