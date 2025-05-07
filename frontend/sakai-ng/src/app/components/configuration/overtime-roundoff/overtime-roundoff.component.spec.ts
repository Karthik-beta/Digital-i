import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OvertimeRoundoffComponent } from './overtime-roundoff.component';

describe('OvertimeRoundoffComponent', () => {
  let component: OvertimeRoundoffComponent;
  let fixture: ComponentFixture<OvertimeRoundoffComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [OvertimeRoundoffComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(OvertimeRoundoffComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
