import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MachineAllocationComponent } from './machine-allocation.component';

describe('MachineAllocationComponent', () => {
  let component: MachineAllocationComponent;
  let fixture: ComponentFixture<MachineAllocationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MachineAllocationComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MachineAllocationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
