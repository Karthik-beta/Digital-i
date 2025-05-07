import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FixedShiftComponent } from './fixed-shift.component';

describe('FixedShiftComponent', () => {
  let component: FixedShiftComponent;
  let fixture: ComponentFixture<FixedShiftComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [FixedShiftComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(FixedShiftComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
