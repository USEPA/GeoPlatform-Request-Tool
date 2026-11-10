import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ChooseCreationMethodComponent } from './choose-creation-method.component';
import {MAT_DIALOG_DATA, MatDialogModule, MatDialogRef} from '@angular/material/dialog';

describe('ChooseCreationMethodComponent', () => {
  let component: ChooseCreationMethodComponent;
  let fixture: ComponentFixture<ChooseCreationMethodComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ChooseCreationMethodComponent ],
      imports: [
        MatDialogModule,
      ],
      providers: [
        {provide: MatDialogRef, useValue: {}},
        {provide: MAT_DIALOG_DATA, useValue: {}}
      ]
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
