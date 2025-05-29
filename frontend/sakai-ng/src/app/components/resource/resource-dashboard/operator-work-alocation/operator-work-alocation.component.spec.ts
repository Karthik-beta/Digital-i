import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OperatorWorkAlocationComponent } from './operator-work-alocation.component';

describe('OperatorWorkAlocationComponent', () => {
  let component: OperatorWorkAlocationComponent;
  let fixture: ComponentFixture<OperatorWorkAlocationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OperatorWorkAlocationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OperatorWorkAlocationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
