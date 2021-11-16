import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ChooseCreationMethodComponent } from './choose-creation-method.component';

describe('ChooseCreationMethodComponent', () => {
  let component: ChooseCreationMethodComponent;
  let fixture: ComponentFixture<ChooseCreationMethodComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ChooseCreationMethodComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ChooseCreationMethodComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
