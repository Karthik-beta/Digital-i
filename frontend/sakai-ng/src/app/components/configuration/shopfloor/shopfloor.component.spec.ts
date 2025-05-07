import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ShopfloorComponent } from './shopfloor.component';

describe('ShopfloorComponent', () => {
  let component: ShopfloorComponent;
  let fixture: ComponentFixture<ShopfloorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ShopfloorComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ShopfloorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
