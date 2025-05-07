import { Component, OnInit } from '@angular/core';
import { SharedService } from 'src/app/shared.service';

@Component({
  selector: 'app-absence-correction',
  templateUrl: './absence-correction.component.html',
  styleUrl: './absence-correction.component.scss'
})
export class AbsenceCorrectionComponent implements OnInit {

    id: number = 0;

    enable_feature: boolean = false;

    cutoff_time: Date = new Date();

    constructor(private service:SharedService) {}

    ngOnInit() {
        this.getAbsenceCorrectionSettings();
    }

    convertTo24HourFormat(date: Date): string {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = '00';
        return `${hours}:${minutes}:${seconds}`;
    }

    getAbsenceCorrectionSettings() {
        this.service.getAutoAbsenceCorrectionSettings().subscribe((data:any) => {
            this.id = data.id;
            this.enable_feature = data.is_enabled;
            this.cutoff_time = new Date(`1970-01-01T${data.cutoff_time}`);
        });
    }

    onCutoffTimeChange(event: any) {

        const formData = {
            id: this.id,
            is_enabled: this.enable_feature,
            cutoff_time: this.convertTo24HourFormat(new Date(event.target.value))
        }

        this.service.updateAutoAbsenceCorrectionSettings(this.id, formData).subscribe((data:any) => {
            console.log(data);
        });

    }



}
