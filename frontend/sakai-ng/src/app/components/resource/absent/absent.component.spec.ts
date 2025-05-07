import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AbsentComponent } from './absent.component';

describe('AbsentComponent', () => {
  let component: AbsentComponent;
  let fixture: ComponentFixture<AbsentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AbsentComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(AbsentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
