import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmpAtendenceComponent } from './emp-atendence.component';

describe('EmpAtendenceComponent', () => {
  let component: EmpAtendenceComponent;
  let fixture: ComponentFixture<EmpAtendenceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EmpAtendenceComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EmpAtendenceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
