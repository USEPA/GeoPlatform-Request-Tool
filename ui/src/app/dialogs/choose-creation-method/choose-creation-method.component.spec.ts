import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ChooseCreationMethodComponent } from './choose-creation-method.component';
import {MAT_LEGACY_DIALOG_DATA, MatLegacyDialogModule, MatLegacyDialogRef} from '@angular/material/legacy-dialog';

describe('ChooseCreationMethodComponent', () => {
  let component: ChooseCreationMethodComponent;
  let fixture: ComponentFixture<ChooseCreationMethodComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ChooseCreationMethodComponent ],
      imports: [
        MatLegacyDialogModule,
      ],
      providers: [
        {provide: MatLegacyDialogRef, useValue: {}},
        {provide: MAT_LEGACY_DIALOG_DATA, useValue: {}}
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
