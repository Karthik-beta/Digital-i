import { Component, OnInit } from '@angular/core';
import { SelectButtonModule } from 'primeng/selectbutton';

@Component({
  selector: 'app-shift-skill',
  standalone: false,
//   imports: [],
  templateUrl: './shift-skill.component.html',
  styleUrl: './shift-skill.component.scss'
})
export class ShiftSkillComponent implements OnInit {


    value: number[] = [1, 2, 3]

    cardOptions: any[] = [
        { name: 'INDUCTION', value: 1 },
        { name: 'BOTTLE', value: 2 },
        { name: 'COOKER', value: 3 }
    ];

    ngOnInit(): void {

    }

    selectedEmployeeSubAssembly: string='';
    selectedEmployeeSubAssembly2: string='';
    selectedEmployeeMainAssembly: string='';
    selectedEmployeeInstallationTesting: string='';

    employeeOptions: string[] = [
        'SURESH, 002',
        // Add more employee options here if needed
    ];

    dummyList1: any[] = [
        {
            operations1: 'PL-01',
            skill_matrix1: 'TEST',
            sso1: 'Krishna , 223044348',
            status1: 'P - 06:34:00',
            sub_emp1: '',
        },
        // {
        //     operations1: 'PL-02, Cable Tie base Assembly',
        //     skill_matrix1: 'AXIAL DRIVE Testing',
        //     sso: 'Suma HC, 212437037',
        //     status1: 'P - 06:35:34<',
        //     sub_emp1: '',
        // },
        // {
        //     operations1: 'PL-03, Bearing Grease nipple assembly on bearing',
        //     skill_matrix1: 'ORP Sub-Assembly',
        //     sso: 'Geetha BP, 305008438',
        //     status1: 'P - 06:34:00',
        //     sub_emp1: '',
        // },
        // {
        //     operations1: '',
        //     skill_matrix1: '',
        //     sso: '',
        //     status1: '',
        //     sub_emp1: '',
        // },
        // {
        //     operations1: '',
        //     skill_matrix1: '',
        //     sso: '',
        //     status1: '',
        //     sub_emp1: '',
        // }
    ]

    dummyList2: any[] = [
        {
            operations2: 'PL-01',
            skill_matrix2: 'TEST',
            sso2: 'Sharath SB, 223098308',
            status2: 'P - 06:32:11',
            sub_emp2: '',
        }
    ]

}

