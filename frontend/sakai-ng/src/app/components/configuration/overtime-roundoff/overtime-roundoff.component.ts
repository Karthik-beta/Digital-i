import { Component, OnInit } from '@angular/core';
import { SharedService } from 'src/app/shared.service';
import { MessageService, ConfirmationService } from 'primeng/api';

interface Direction {
    name: string;
}

@Component({
  selector: 'app-overtime-roundoff',
  templateUrl: './overtime-roundoff.component.html',
  styleUrl: './overtime-roundoff.component.scss'
})
export class OvertimeRoundoffComponent implements OnInit {

    rulesList: any[] = [];

    ModalTitle:string="Edit Rules";
    display: boolean = false;
    loading: boolean = true;

    id: number=0;
    round_off_interval: Number | undefined;
    round_off_direction: string='';

    direction: Direction[] | undefined;
    selectedDirection: string = '';

    constructor(private service:SharedService,
            private messageService: MessageService) { }

    ngOnInit() {
        this.getovertimeRulesList();

        this.direction = [
            { name: 'Up' },
            { name: 'Nearest' },
            { name: 'Down' }
        ]
    }

    convertTo24HourFormat(date: Date): string {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = '00';
        return `${hours}:${minutes}:${seconds}`;
    }

    getovertimeRulesList() {
        this.loading = true;

        this.service.getOvertimeRulesList().subscribe((data) => {
            // Ensure the response is always an array
            this.rulesList = Array.isArray(data) ? data : [data];
            this.loading = false;
        });

    }

    EditClick() {
        this.display = true;
        this.loadData();
    }

    loadData() {
        this.id = this.rulesList[0].id;
        this.round_off_interval = this.rulesList[0].round_off_interval;
        this.round_off_direction = this.rulesList[0].round_off_direction;

        // Find and set the selected direction as an object
        const directionObj = this.direction?.find(dir => dir.name === this.rulesList[0].round_off_direction);
        this.selectedDirection = directionObj ? directionObj.name : '';
    }

    assignDirection(selectedDirection: any) {
        this.round_off_direction = selectedDirection.name;
        console.log(this.selectedDirection);
    }

    updateRules() {
        const val = {
            id: this.id,
            round_off_interval: this.round_off_interval,
            round_off_direction: this.round_off_direction
        };

        console.log(val);

        this.service.updateOvertimeRules(this.id, val).subscribe(data => {
            this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Rules Updated' });
            this.getovertimeRulesList();
            this.display = false;
        });
    }


}
