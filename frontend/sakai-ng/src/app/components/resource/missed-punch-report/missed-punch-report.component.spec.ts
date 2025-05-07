import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MissedPunchReportComponent } from './missed-punch-report.component';

describe('MissedPunchReportComponent', () => {
  let component: MissedPunchReportComponent;
  let fixture: ComponentFixture<MissedPunchReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MissedPunchReportComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MissedPunchReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
