import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FoodCourtComponent } from './food-court.component';

describe('FoodCourtComponent', () => {
  let component: FoodCourtComponent;
  let fixture: ComponentFixture<FoodCourtComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FoodCourtComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FoodCourtComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
