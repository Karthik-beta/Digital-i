import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LateEntryComponent } from './late-entry.component';

describe('LateEntryComponent', () => {
  let component: LateEntryComponent;
  let fixture: ComponentFixture<LateEntryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LateEntryComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LateEntryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
