import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestFieldCoordDialogComponent } from './request-field-coord-dialog.component';
import {MAT_LEGACY_DIALOG_DATA, MatLegacyDialogRef} from '@angular/material/legacy-dialog';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {LoadingService} from '@services/loading.service';

describe('RequestFieldCoordDialogComponent', () => {
  let component: RequestFieldCoordDialogComponent;
  let fixture: ComponentFixture<RequestFieldCoordDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestFieldCoordDialogComponent ],
      imports: [
        HttpClientTestingModule
      ],
      providers: [
        {provide: MatLegacyDialogRef, useValue: {}},
        {provide: LoadingService, useValue: {}},
        {provide: MAT_LEGACY_DIALOG_DATA, useValue: {}}
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestFieldCoordDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
