import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OperatorWorkAllocationComponent } from './operator-work-allocation.component';

describe('OperatorWorkAllocationComponent', () => {
  let component: OperatorWorkAllocationComponent;
  let fixture: ComponentFixture<OperatorWorkAllocationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [OperatorWorkAllocationComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(OperatorWorkAllocationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
