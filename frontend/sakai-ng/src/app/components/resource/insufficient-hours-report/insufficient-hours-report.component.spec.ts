import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InsufficientHoursReportComponent } from './insufficient-hours-report.component';

describe('InsufficientHoursReportComponent', () => {
  let component: InsufficientHoursReportComponent;
  let fixture: ComponentFixture<InsufficientHoursReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [InsufficientHoursReportComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(InsufficientHoursReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
