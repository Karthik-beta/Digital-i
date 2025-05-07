import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MonthlyInOutComponent } from './monthly-in-out.component';

describe('MonthlyInOutComponent', () => {
  let component: MonthlyInOutComponent;
  let fixture: ComponentFixture<MonthlyInOutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MonthlyInOutComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MonthlyInOutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
