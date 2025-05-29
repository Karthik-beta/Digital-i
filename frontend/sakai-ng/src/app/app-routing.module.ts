import { RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';
import { NotfoundComponent } from './demo/components/notfound/notfound.component';
import { AppLayoutComponent } from "./layout/app.layout.component";
import { authGuard } from './guards/auth.guard';

import { ShiftSkillComponent } from './components/resource/resource-dashboard/shift-skill/shift-skill.component';
import { ConfigComponent } from './components/configuration/config/config.component';
import { EmployeeMasterComponent } from './components/resource/employee-master/employee-master.component';
import { DailyReportComponent } from './components/resource/daily-report/daily-report.component';
import { ShiftStrengthComponent } from './components/resource/resource-dashboard/shift-strength/shift-strength.component';
import { AddEditEmployeeComponent } from './components/resource/employee-master/add-edit-employee/add-edit-employee.component';
import { MonthlyInOutComponent } from './components/resource/monthly-in-out/monthly-in-out.component';
// import { MissedPunchComponent } from './components/resource/attendance-reg/missed-punch/missed-punch.component';
import { AbsentComponent } from './components/resource/absent/absent.component';
import { LateEntryComponent } from './components/resource/late-entry/late-entry.component';
import { EarlyExitComponent } from './components/resource/early-exit/early-exit.component';
import { OvertimeComponent } from './components/resource/overtime/overtime.component';
import { PresentComponent } from './components/resource/present/present.component';
import { MissedPunchReportComponent } from './components/resource/missed-punch-report/missed-punch-report.component';
import { InsufficientHoursReportComponent } from './components/resource/insufficient-hours-report/insufficient-hours-report.component';
import { MandaysComponent } from './components/resource/mandays/mandays.component';
import { LogsComponent } from './components/configurations/logs/logs.component';
import { MissedPunchComponent } from './components/resource/attendance-regularization/missed-punch/missed-punch.component';
import { DeviceConfigComponent } from './components/configuration/device-config/device-config.component';
import { ResetReportComponent } from './components/resource/reset-report/reset-report.component';
import { EmpAtendenceComponent } from './components/resource/attendance-regularization/emp-atendence/emp-atendence.component';
import { MachineAllocationComponent } from './components/resource/attendance-regularization/machine-allocation/machine-allocation.component';
import { EmpStrengthComponent } from './components/resource/resource-dashboard/emp-strength/emp-strength.component';
import { evacuationComponent } from './components/resource/resource-dashboard/evacuation/evacuation.component';
import { EmpIntervalStrengthComponent } from './components/resource/resource-dashboard/emp-interval-strength/emp-interval-strength.component';
import { DepStrengthComponent } from './components/resource/resource-dashboard/dep-strength/dep-strength.component';
import { AgencyStrengthComponent } from './components/resource/resource-dashboard/agency-strength/agency-strength.component';
import { OperatorWorkAlocationComponent } from './components/resource/resource-dashboard/operator-work-alocation/operator-work-alocation.component';
import { FoodCourtComponent } from './components/resource/resource-dashboard/food-court/food-court.component';
import { HeadcountComponent } from './components/resource/resource-dashboard/headcount/headcount.component';

@NgModule({
    imports: [
        RouterModule.forRoot([
            // { path: '', redirectTo: 'auth/login', pathMatch: 'full' },
            {
                path: '', component: AppLayoutComponent,
                children: [
                    { path: '', loadChildren: () => import('./demo/components/dashboard/dashboard.module').then(m => m.DashboardModule), canActivate: [authGuard] },
                    { path: 'uikit', loadChildren: () => import('./demo/components/uikit/uikit.module').then(m => m.UIkitModule), canActivate: [authGuard] },
                    { path: 'utilities', loadChildren: () => import('./demo/components/utilities/utilities.module').then(m => m.UtilitiesModule), canActivate: [authGuard] },
                    { path: 'documentation', loadChildren: () => import('./demo/components/documentation/documentation.module').then(m => m.DocumentationModule), canActivate: [authGuard] },
                    { path: 'blocks', loadChildren: () => import('./demo/components/primeblocks/primeblocks.module').then(m => m.PrimeBlocksModule), canActivate: [authGuard] },
                    { path: 'pages', loadChildren: () => import('./demo/components/pages/pages.module').then(m => m.PagesModule), canActivate: [authGuard] },

                    { path: 'shift_skill', component: ShiftSkillComponent, canActivate: [authGuard] },

                    // Resource
                    { path: 'employee_master', component: EmployeeMasterComponent, canActivate: [authGuard] },
                    { path: 'add_employee', component: AddEditEmployeeComponent, canActivate: [authGuard] },
                    { path: 'view_edit_employee/:id', component: AddEditEmployeeComponent, canActivate: [authGuard] },
                    { path: 'daily_report', component: DailyReportComponent, canActivate: [authGuard] },
                    { path: 'present_report', component: PresentComponent, canActivate: [authGuard] },
                    { path: 'absent_report', component: AbsentComponent, canActivate: [authGuard] },
                    { path: 'late_entry_report', component: LateEntryComponent, canActivate: [authGuard] },
                    { path: 'early_exit_report', component: EarlyExitComponent, canActivate: [authGuard] },
                    { path: 'overtime_report', component: OvertimeComponent, canActivate: [authGuard] },
                    { path: 'missed_punch_report', component: MissedPunchReportComponent, canActivate: [authGuard] },
                    { path: 'insufficient_hours_report', component: InsufficientHoursReportComponent, canActivate: [authGuard] },
                    { path: 'Monthly_In_Out', component: MonthlyInOutComponent, canActivate: [authGuard] },
                    { path: 'shift_strength', component: ShiftStrengthComponent, canActivate: [authGuard] },
                    // { path: 'missed_punch', component: MissedPunchComponent, canActivate: [authGuard] },
                    { path: 'mandays_report', component: MandaysComponent, canActivate: [authGuard] },

                    // Attendance Regularization
                    { path: 'missed_punch', component: MissedPunchComponent, canActivate: [authGuard] },
                    // { path: 'missed_punch_2', component: MissedPunchComponent, canActivate: [authGuard] },


                    // Configuration
                    { path: 'configuration', component: ConfigComponent, canActivate: [authGuard] },
                    { path: 'logs', component: LogsComponent, canActivate: [authGuard] },

                    // Evacuation

                    { path: 'device_config', component: DeviceConfigComponent, canActivate: [authGuard] },
                    { path: 'reset_report', component: ResetReportComponent, canActivate: [authGuard] },

                    { path: 'emp_attendance', component: EmpAtendenceComponent, canActivate: [authGuard] },
                    { path: 'machine_allocation', component: MachineAllocationComponent, canActivate: [authGuard] },

                    { path: 'employee_strength', component: EmpStrengthComponent, canActivate: [authGuard] },
                    { path: 'evacuation_manage', component: evacuationComponent, canActivate: [authGuard] },
                    { path: 'employee_interval_strength', component: EmpIntervalStrengthComponent, canActivate: [authGuard] },
                    { path: 'dep_strength', component: DepStrengthComponent, canActivate: [authGuard] },
                    { path: 'agency_strength', component: AgencyStrengthComponent, canActivate: [authGuard] },
                    { path: 'op_work_allocation', component: OperatorWorkAlocationComponent, canActivate: [authGuard] },
                    { path: 'food_court', component: FoodCourtComponent, canActivate: [authGuard] },
                    { path: 'headcount_manage', component: HeadcountComponent, canActivate: [authGuard] },
                ]
            },
            { path: 'auth', loadChildren: () => import('./demo/components/auth/auth.module').then(m => m.AuthModule) },
            { path: 'landing', loadChildren: () => import('./demo/components/landing/landing.module').then(m => m.LandingModule) },
            { path: 'notfound', component: NotfoundComponent },
            { path: '**', redirectTo: '/notfound' },
        ], { scrollPositionRestoration: 'enabled', anchorScrolling: 'enabled', onSameUrlNavigation: 'reload' })
    ],
    exports: [RouterModule]
})
export class AppRoutingModule {
}
