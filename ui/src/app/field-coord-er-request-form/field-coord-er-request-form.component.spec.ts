import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FieldCoordErRequestFormComponent } from './field-coord-er-request-form.component';

describe('FieldCoordErRequestFormComponent', () => {
  let component: FieldCoordErRequestFormComponent;
  let fixture: ComponentFixture<FieldCoordErRequestFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FieldCoordErRequestFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FieldCoordErRequestFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
