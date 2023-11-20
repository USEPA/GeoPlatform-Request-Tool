import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {ApprovalListComponent} from './approval-list.component';
import {MatTableModule} from '@angular/material';
import {Observable, of} from 'rxjs';
import {MatLegacyDialog as MatDialog} from '@angular/material/legacy-dialog';
import {FilterInputComponent} from '../filter-input/filter-input.component';
import {CustomMaterialModule} from '../core/material.module';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {CdkTableModule} from '@angular/cdk/table';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {LoadingService} from '@services/loading.service';
import {LoginService} from '../auth/login.service';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatLegacySnackBar as MatSnackBar} from '@angular/material/legacy-snack-bar';

import {environment} from '@environments/environment';
// @ts-ignore
import * as mockData from './approval-list-mock-data.json';



class MatDialogMock {
  public open() {
    return {afterClosed: () => of({confirmed: true})};
  }
}

class MatSnackBarStub {
  open() {
    return {
      onAction: () => of({})
    };
  }
}

describe('ApprovalListComponent', () => {
  let component: ApprovalListComponent;
  let fixture: ComponentFixture<ApprovalListComponent>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;
  let matSnackBar: MatSnackBar;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        CustomMaterialModule,
        FormsModule,
        ReactiveFormsModule,
        MatTableModule,
        CdkTableModule,
        HttpClientTestingModule,
        BrowserAnimationsModule
      ],
      declarations: [ApprovalListComponent, FilterInputComponent],
      providers: [
        {provide: MatDialog, useClass: MatDialogMock},
        {provide: LoadingService, useValue: {setLoading: () => null}},
        {provide: LoginService, useValue: {}},
        {provide: MatSnackBar, useClass: MatSnackBarStub}
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ApprovalListComponent);
    component = fixture.componentInstance;
    matSnackBar = TestBed.get(MatSnackBar);
    httpTestingController = TestBed.get(HttpTestingController);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should notify users of successful approval', () => {
    spyOn(matSnackBar, 'open');
    spyOn(component.accounts, 'getItems').and.returnValue(of([{}]));
    component.confirmApproval();
    const req = httpTestingController.expectOne('/v1/account/approvals/approve/');
    req.flush('');
    expect(matSnackBar.open).toHaveBeenCalledWith('Success', null, Object({ duration: 2000 }));
  });

  it('should notify users of error if returned from server', () => {
    spyOn(matSnackBar, 'open');
    spyOn(component.accounts, 'getItems').and.returnValue(of([{}]));
    component.confirmApproval();
    const req = httpTestingController.expectOne('/v1/account/approvals/approve/');
    const errorResponse = new HttpErrorResponse({error: 'error', status: 403});
    req.flush('', errorResponse);
    expect(matSnackBar.open).toHaveBeenCalledWith('Error', null, {duration: 3000});
  });

  it('should notify users of successful approval update with group as property', () => {
    spyOn(matSnackBar, 'open');
    spyOn(component, 'setNeedsEditing').and.callFake((param) => {
      expect(param).toBe(mockData.updateApprovalTest);
    });
    component.updateRecord(mockData.updateApprovalTest).subscribe();
    const url = `/v1/account/approvals/${mockData.updateApprovalTest.id}/`;
    const req = httpTestingController.expectOne(url);
    expect(req.request.method).toBe('PUT');
    req.flush(mockData.updateApprovalTest);
    expect(matSnackBar.open).toHaveBeenCalledWith('Success', null, Object({ duration: 2000 }));
  });
});
