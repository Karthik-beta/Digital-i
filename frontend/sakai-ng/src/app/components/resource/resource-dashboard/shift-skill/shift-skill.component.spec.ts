import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ShiftSkillComponent } from './shift-skill.component';

describe('ShiftSkillComponent', () => {
  let component: ShiftSkillComponent;
  let fixture: ComponentFixture<ShiftSkillComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ShiftSkillComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ShiftSkillComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
