import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MissedPunchComponent } from './missed-punch.component';

describe('MissedPunchComponent', () => {
  let component: MissedPunchComponent;
  let fixture: ComponentFixture<MissedPunchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MissedPunchComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MissedPunchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
