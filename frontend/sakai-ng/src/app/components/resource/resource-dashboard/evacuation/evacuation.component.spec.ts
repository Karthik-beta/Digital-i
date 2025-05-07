import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EvacuationComponent } from './evacuation.component';

describe('EvacuationComponent', () => {
  let component: EvacuationComponent;
  let fixture: ComponentFixture<EvacuationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EvacuationComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EvacuationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
