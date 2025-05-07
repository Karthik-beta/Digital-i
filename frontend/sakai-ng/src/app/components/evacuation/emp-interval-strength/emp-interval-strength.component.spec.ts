import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmpIntervalStrengthComponent } from './emp-interval-strength.component';

describe('EmpIntervalStrengthComponent', () => {
  let component: EmpIntervalStrengthComponent;
  let fixture: ComponentFixture<EmpIntervalStrengthComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EmpIntervalStrengthComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EmpIntervalStrengthComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
