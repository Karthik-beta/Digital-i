import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EarlyExitComponent } from './early-exit.component';

describe('EarlyExitComponent', () => {
  let component: EarlyExitComponent;
  let fixture: ComponentFixture<EarlyExitComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EarlyExitComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EarlyExitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
