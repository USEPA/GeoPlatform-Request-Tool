import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FieldCoordListComponent } from './field-coord-list.component';

describe('FieldCoordListComponent', () => {
  let component: FieldCoordListComponent;
  let fixture: ComponentFixture<FieldCoordListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FieldCoordListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FieldCoordListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
