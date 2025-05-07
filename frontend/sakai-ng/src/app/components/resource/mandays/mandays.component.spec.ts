import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MandaysComponent } from './mandays.component';

describe('MandaysComponent', () => {
  let component: MandaysComponent;
  let fixture: ComponentFixture<MandaysComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MandaysComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MandaysComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
