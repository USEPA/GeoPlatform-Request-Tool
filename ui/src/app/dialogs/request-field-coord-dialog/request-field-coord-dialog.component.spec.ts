import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestFieldCoordDialogComponent } from './request-field-coord-dialog.component';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
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
        {provide: MatDialogRef, useValue: {}},
        {provide: LoadingService, useValue: {}},
        {provide: MAT_DIALOG_DATA, useValue: {}}
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
