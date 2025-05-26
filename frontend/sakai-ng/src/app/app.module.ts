import { NgModule, isDevMode } from '@angular/core';
import { HashLocationStrategy, LocationStrategy, PathLocationStrategy } from '@angular/common';
import { DatePipe } from '@angular/common';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { AppLayoutModule } from './layout/app.layout.module';
import { NotfoundComponent } from './demo/components/notfound/notfound.component';
import { ProductService } from './demo/service/product.service';
import { CountryService } from './demo/service/country.service';
import { CustomerService } from './demo/service/customer.service';
import { EventService } from './demo/service/event.service';
import { IconService } from './demo/service/icon.service';
import { NodeService } from './demo/service/node.service';
import { PhotoService } from './demo/service/photo.service';
import { BrowserModule } from '@angular/platform-browser';
import { SharedService } from './shared.service';
import { MessageService } from 'primeng/api';
import { ConfirmationService } from 'primeng/api';


import { DropdownModule } from "primeng/dropdown";
import { SelectButtonModule } from 'primeng/selectbutton';
import { CardModule } from 'primeng/card';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ChartModule } from 'primeng/chart';
import { MenuModule } from 'primeng/menu';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { StyleClassModule } from 'primeng/styleclass';
import { PanelMenuModule } from 'primeng/panelmenu';
import { DialogModule } from 'primeng/dialog';
import { InputMaskModule } from "primeng/inputmask";
import { InputNumberModule } from "primeng/inputnumber";
import { InputTextModule } from "primeng/inputtext";
import { SplitButtonModule } from 'primeng/splitbutton';
import { UIkitModule } from './demo/components/uikit/uikit.module';
import { ToggleButtonModule } from 'primeng/togglebutton';
import { DividerModule } from 'primeng/divider';
import { DockModule } from 'primeng/dock';
import { ProgressBarModule } from 'primeng/progressbar';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { TooltipModule } from 'primeng/tooltip';
import { KeyFilterModule } from 'primeng/keyfilter';
import { FieldsetModule } from 'primeng/fieldset';
import { TagModule } from 'primeng/tag';
import { StepperModule } from 'primeng/stepper';
import { StepsModule } from 'primeng/steps';
import { FloatLabelModule } from 'primeng/floatlabel';

// Import PrimeNG modules
import { AccordionModule } from 'primeng/accordion';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { AvatarModule } from 'primeng/avatar';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { BadgeModule } from 'primeng/badge';
import { BreadcrumbModule } from 'primeng/breadcrumb';
import { CalendarModule } from 'primeng/calendar';
import { CarouselModule } from 'primeng/carousel';
import { CascadeSelectModule } from 'primeng/cascadeselect';
import { CheckboxModule } from 'primeng/checkbox';
import { ChipModule } from 'primeng/chip';
import { ChipsModule } from 'primeng/chips';
import { ConfirmPopupModule } from 'primeng/confirmpopup';
import { ColorPickerModule } from 'primeng/colorpicker';
import { ContextMenuModule } from 'primeng/contextmenu';
import { DataViewModule } from 'primeng/dataview';
import { VirtualScrollerModule } from 'primeng/virtualscroller';
import { DragDropModule } from 'primeng/dragdrop';
import { DynamicDialogModule } from 'primeng/dynamicdialog';
import { EditorModule } from 'primeng/editor';
import { FileUploadModule } from 'primeng/fileupload';
import { GalleriaModule } from 'primeng/galleria';
import { InplaceModule } from 'primeng/inplace';
import { InputSwitchModule } from 'primeng/inputswitch';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { InputGroupAddonModule } from 'primeng/inputgroupaddon';
import { InputGroupModule } from 'primeng/inputgroup'
import { InputOtpModule } from 'primeng/inputotp'
import { ImageModule } from 'primeng/image';
import { KnobModule } from 'primeng/knob';
import { ListboxModule } from 'primeng/listbox';
import { MegaMenuModule } from 'primeng/megamenu';
import { MenubarModule } from 'primeng/menubar';
import { MessageModule } from 'primeng/message';
import { MessagesModule } from 'primeng/messages';
import { MultiSelectModule } from 'primeng/multiselect';
import { MeterGroupModule } from 'primeng/metergroup';
import { OrderListModule } from 'primeng/orderlist';
import { OrganizationChartModule } from 'primeng/organizationchart';
import { OverlayPanelModule } from 'primeng/overlaypanel';
import { PaginatorModule } from 'primeng/paginator';
import { PanelModule } from 'primeng/panel';
import { PasswordModule } from 'primeng/password';
import { PickListModule } from 'primeng/picklist';
import { RadioButtonModule } from 'primeng/radiobutton';
import { RatingModule } from 'primeng/rating';
import { ScrollerModule } from 'primeng/scroller';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { ScrollTopModule } from 'primeng/scrolltop';
import { SidebarModule } from 'primeng/sidebar';
import { SkeletonModule } from 'primeng/skeleton';
import { SlideMenuModule } from 'primeng/slidemenu';
import { SliderModule } from 'primeng/slider';
import { SpeedDialModule } from 'primeng/speeddial';
import { SpinnerModule } from 'primeng/spinner';
import { SplitterModule } from 'primeng/splitter';
import { TabMenuModule } from 'primeng/tabmenu';
import { TabViewModule } from 'primeng/tabview';
import { TerminalModule } from 'primeng/terminal';
import { TieredMenuModule } from 'primeng/tieredmenu';
import { TimelineModule } from 'primeng/timeline';
import { ToolbarModule } from 'primeng/toolbar';
import { TriStateCheckboxModule } from 'primeng/tristatecheckbox';
import { TreeModule } from 'primeng/tree';
import { TreeSelectModule } from 'primeng/treeselect';
import { TreeTableModule } from 'primeng/treetable';
import { AnimateModule } from 'primeng/animate';
import { BlockUIModule } from 'primeng/blockui';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { RippleModule } from 'primeng/ripple';
import { AutoFocusModule } from 'primeng/autofocus';

import { EmployeeMasterComponent } from './components/resource/employee-master/employee-master.component';
import { ShiftSkillComponent } from './components/resource/resource-dashboard/shift-skill/shift-skill.component';
import { ConfigComponent } from './components/configuration/config/config.component';
import { DailyReportComponent } from './components/resource/daily-report/daily-report.component';
import { ShiftStrengthComponent } from './components/resource/resource-dashboard/shift-strength/shift-strength.component';
import { EvacuationComponent } from './components/resource/resource-dashboard/evacuation/evacuation.component';
import { AddEditEmployeeComponent } from './components/resource/employee-master/add-edit-employee/add-edit-employee.component';
import { CompanyComponent } from './components/configuration/company/company.component';
import { LocationComponent } from './components/configuration/location/location.component';
import { DepartmentComponent } from './components/configuration/department/department.component';
import { DesignationComponent } from './components/configuration/designation/designation.component';
import { DivisionComponent } from './components/configuration/division/division.component';
import { SubdivisionComponent } from './components/configuration/subdivision/subdivision.component';
import { ShopfloorComponent } from './components/configuration/shopfloor/shopfloor.component';
import { MonthlyInOutComponent } from './components/resource/monthly-in-out/monthly-in-out.component';
import { ServiceWorkerModule } from '@angular/service-worker';

// import { MissedPunchComponent } from './components/resource/attendance-reg/missed-punch/missed-punch.component';
import { MissedPunchComponent } from './components/resource/attendance-regularization/missed-punch/missed-punch.component';
import { ShiftComponent } from './components/configuration/shift/shift.component';
import { AbsentComponent } from './components/resource/absent/absent.component';
import { LateEntryComponent } from './components/resource/late-entry/late-entry.component';
import { EarlyExitComponent } from './components/resource/early-exit/early-exit.component';
import { OvertimeComponent } from './components/resource/overtime/overtime.component';
import { PresentComponent } from './components/resource/present/present.component';
import { MissedPunchReportComponent } from './components/resource/missed-punch-report/missed-punch-report.component';
import { InsufficientHoursReportComponent } from './components/resource/insufficient-hours-report/insufficient-hours-report.component';
import { MandaysComponent } from './components/resource/mandays/mandays.component';
import { LogsComponent } from './components/configurations/logs/logs.component';
import { FixedShiftComponent } from './components/configuration/fixed-shift/fixed-shift.component';
import { OvertimeRoundoffComponent } from './components/configuration/overtime-roundoff/overtime-roundoff.component';
import { HolidayListComponent } from './components/configuration/holiday-list/holiday-list.component';
import { AbsenceCorrectionComponent } from './components/configuration/absence-correction/absence-correction.component';
import { AgencyStrengthComponent } from './components/evacuation/agency-strength/agency-strength.component';
import { DepStrengthComponent } from './components/evacuation/dep-strength/dep-strength.component';
import { EmpIntervalStrengthComponent } from './components/evacuation/emp-interval-strength/emp-interval-strength.component';
import { EmpStrengthComponent } from './components/evacuation/emp-strength/emp-strength.component';
import { FoodCourtComponent } from './components/evacuation/food-court/food-court.component';
import { OperatorWorkAllocationComponent } from './components/evacuation/operator-work-allocation/operator-work-allocation.component';
import { DeviceConfigComponent } from './components/configuration/device-config/device-config.component';
import { ResetReportComponent } from './components/resource/reset-report/reset-report.component';
import { EmpAtendenceComponent } from './components/resource/attendance-regularization/emp-atendence/emp-atendence.component';
import { MachineAllocationComponent } from './components/resource/attendance-regularization/machine-allocation/machine-allocation.component';




@NgModule({
    declarations: [
        AppComponent, NotfoundComponent, EmployeeMasterComponent, AddEditEmployeeComponent, ShiftSkillComponent, ConfigComponent,
        DailyReportComponent, ShiftStrengthComponent, EvacuationComponent, CompanyComponent, LocationComponent, LocationComponent,
        DepartmentComponent, DesignationComponent, DivisionComponent, SubdivisionComponent, ShopfloorComponent, MonthlyInOutComponent,
        MissedPunchComponent,
        ShiftComponent,
        AbsentComponent,
        LateEntryComponent,
        EarlyExitComponent,
        OvertimeComponent,
        PresentComponent,
        MissedPunchReportComponent,
        InsufficientHoursReportComponent,
        MandaysComponent,
        LogsComponent,
        FixedShiftComponent,
        OvertimeRoundoffComponent,
        HolidayListComponent,
        AbsenceCorrectionComponent,
        AgencyStrengthComponent,
        DepStrengthComponent,
        EmpIntervalStrengthComponent,
        EmpStrengthComponent,
        FoodCourtComponent,
        OperatorWorkAllocationComponent,
        DeviceConfigComponent,
        ResetReportComponent,
    ],
    imports: [
        AppRoutingModule,
        AppLayoutModule,

        DropdownModule,
        SelectButtonModule,
        CardModule,
        BrowserModule,
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        ChartModule,
        MenuModule,
        TableModule,
        ButtonModule,
        StyleClassModule,
        PanelMenuModule,
        DialogModule,
        InputMaskModule,
        InputNumberModule,
        InputTextModule,
        SplitButtonModule,
        UIkitModule,
        ToggleButtonModule,
        DividerModule,
        DockModule,
        ProgressBarModule,
        ConfirmDialogModule,
        ToastModule,
        TooltipModule,
        KeyFilterModule,
        FieldsetModule,
        TagModule,
        StepperModule,
        StepsModule,
        FloatLabelModule,
        AccordionModule,
        AutoCompleteModule,
        AvatarModule,
        AvatarGroupModule,
        BadgeModule,
        BreadcrumbModule,
        CalendarModule,
        CarouselModule,
        CascadeSelectModule,
        CheckboxModule,
        ChipModule,
        ChipsModule,
        ConfirmPopupModule,
        ColorPickerModule,
        ContextMenuModule,
        DataViewModule,
        VirtualScrollerModule,
        DragDropModule,
        DynamicDialogModule,
        EditorModule,
        FileUploadModule,
        GalleriaModule,
        InplaceModule,
        InputSwitchModule,
        InputTextareaModule,
        InputGroupAddonModule,
        InputGroupModule,
        InputOtpModule,
        ImageModule,
        KnobModule,
        ListboxModule,
        MegaMenuModule,
        MenubarModule,
        MessageModule,
        MessagesModule,
        MultiSelectModule,
        MeterGroupModule,
        OrderListModule,
        OrganizationChartModule,
        OverlayPanelModule,
        PaginatorModule,
        PanelModule,
        PasswordModule,
        PickListModule,
        RadioButtonModule,
        RatingModule,
        ScrollerModule,
        ScrollPanelModule,
        ScrollTopModule,
        SidebarModule,
        SkeletonModule,
        SlideMenuModule,
        SliderModule,
        SpeedDialModule,
        SpinnerModule,
        SplitterModule,
        TabMenuModule,
        TabViewModule,
        TerminalModule,
        TieredMenuModule,
        TimelineModule,
        ToolbarModule,
        TriStateCheckboxModule,
        TreeModule,
        TreeSelectModule,
        TreeTableModule,
        AnimateModule,
        BlockUIModule,
        ProgressSpinnerModule,
        RippleModule,
        AutoFocusModule,

        EmpAtendenceComponent,
        MachineAllocationComponent,
        ServiceWorkerModule.register('ngsw-worker.js', {
          enabled: !isDevMode(),
          // Register the ServiceWorker as soon as the application is stable
          // or after 30 seconds (whichever comes first).
          registrationStrategy: 'registerWhenStable:30000'
        }),
    ],
    providers: [
        DatePipe,
        { provide: LocationStrategy, useClass: PathLocationStrategy },
        CountryService, CustomerService, EventService, IconService, NodeService,
        PhotoService, ProductService, SharedService, MessageService, ConfirmationService
    ],
    bootstrap: [AppComponent],
})
export class AppModule {}
