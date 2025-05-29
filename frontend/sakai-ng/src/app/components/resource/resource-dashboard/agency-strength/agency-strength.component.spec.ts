
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AgencyStrengthComponent } from './agency-strength.component';

describe('AgencyStrengthComponent', () => {
  let component: AgencyStrengthComponent;
  let fixture: ComponentFixture<AgencyStrengthComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgencyStrengthComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AgencyStrengthComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
