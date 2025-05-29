import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HeadcountComponent } from './headcount.component';

describe('HeadcountComponent', () => {
  let component: HeadcountComponent;
  let fixture: ComponentFixture<HeadcountComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [HeadcountComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(HeadcountComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
