import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmpStrengthComponent } from './emp-strength.component';

describe('EmpStrengthComponent', () => {
  let component: EmpStrengthComponent;
  let fixture: ComponentFixture<EmpStrengthComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EmpStrengthComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EmpStrengthComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
