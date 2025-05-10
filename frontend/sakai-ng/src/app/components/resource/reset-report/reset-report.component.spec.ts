import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResetReportComponent } from './reset-report.component';

describe('ResetReportComponent', () => {
  let component: ResetReportComponent;
  let fixture: ComponentFixture<ResetReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ResetReportComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ResetReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
