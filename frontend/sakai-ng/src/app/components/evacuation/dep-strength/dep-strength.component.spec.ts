import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DepStrengthComponent } from './dep-strength.component';

describe('DepStrengthComponent', () => {
  let component: DepStrengthComponent;
  let fixture: ComponentFixture<DepStrengthComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DepStrengthComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DepStrengthComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
