import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AbsenceCorrectionComponent } from './absence-correction.component';

describe('AbsenceCorrectionComponent', () => {
  let component: AbsenceCorrectionComponent;
  let fixture: ComponentFixture<AbsenceCorrectionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AbsenceCorrectionComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(AbsenceCorrectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
