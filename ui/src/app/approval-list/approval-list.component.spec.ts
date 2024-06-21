import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {Accounts, ApprovalListComponent} from './approval-list.component';
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
import {UpdateApprovalTest} from './approval-list-mock-data';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatListModule} from '@angular/material/list';
import {MatTableModule} from '@angular/material/table';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatInputModule} from '@angular/material/input';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatSelectModule} from '@angular/material/select';

const updateApprovalTest = new UpdateApprovalTest();

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
        MatFormFieldModule,
        MatSidenavModule,
        MatListModule,
        MatTableModule,
        MatPaginatorModule,
        FormsModule,
        ReactiveFormsModule,
        CdkTableModule,
        HttpClientTestingModule,
        BrowserAnimationsModule,
        MatInputModule,
        MatCheckboxModule,
        MatSelectModule
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
    component.selectedAccountIds = [1];
    component.createAccounts();
    const req = httpTestingController.expectOne('/api/v1/account/approvals/approve/');
    req.flush({});
    expect(matSnackBar.open).toHaveBeenCalledWith('Success!', null, {duration: 6000, panelClass: ['snackbar-success']});
  });

  it('should notify users of error if returned from server', () => {
    spyOn(matSnackBar, 'open');
    spyOn(component.accounts, 'getItems').and.returnValue(of([{}]));
    component.selectedAccountIds = [1]
    component.createAccounts();
    const req = httpTestingController.expectOne('/api/v1/account/approvals/approve/');
    const errorResponse = new HttpErrorResponse({error: 'error', status: 403});
    req.flush('', errorResponse);
    expect(matSnackBar.open).toHaveBeenCalledWith(
      'There was and error with one or more account requests', null, {
        duration: 6000,
        panelClass: ['snackbar-error']
      });
  });

  it('should notify users of successful approval update with group as property', () => {
    spyOn(matSnackBar, 'open');
    spyOn(component, 'setNeedsEditing').and.callFake((param) => {
      expect(param).toBe(updateApprovalTest);
    });
    component.updateRecord(updateApprovalTest).subscribe();
    const url = `/api/v1/account/approvals/${updateApprovalTest.id}/`;
    const req = httpTestingController.expectOne(url);
    expect(req.request.method).toBe('PUT');
    req.flush(updateApprovalTest);
    expect(matSnackBar.open).toHaveBeenCalledWith('Success', null, Object({duration: 2000}));
  });

  it('should set needs editing if missing required fields', () => {
    component.accountsListProps = {
      1: {
        first_name: null,
        last_name: null,
        username: null,
        email: null,
        groups: null,
        organization: null,
        reason: null,
        response: null,
        sponsor: null,
        approved: null,
        created: null,
        isChecked: false,
        needsEditing: null,
        is_existing_account: null

      }
    };
    component.setNeedsEditing({id: 1, organization: null})
    expect(component.accountsListProps[1].needsEditing).toBeTruthy();

  })

  it('should mark needs editing true if is existing account and email does not match', () => {
    component.accountsListProps = {
      1: {
        first_name: null,
        last_name: null,
        username: null,
        email: null,
        groups: null,
        organization: null,
        reason: null,
        response: null,
        sponsor: null,
        approved: null,
        created: null,
        isChecked: false,
        needsEditing: null,
        is_existing_account: null

      }
    };
    const spyOnEmailMatches = spyOn(component, 'emailMatchesAccount').and.returnValue(false);
    component.setNeedsEditing({
      id: 1, organization: 1, response: 1, sponsor: 1, reason: 1,
      is_existing_account: true, username_valid: false
    })
    expect(component.accountsListProps[1].needsEditing).toBeTruthy();
  })
  it('should mark needs editing false if is existing account and email does match', () => {
    component.accountsListProps = {
      1: {
        first_name: null,
        last_name: null,
        username: null,
        email: null,
        groups: null,
        organization: null,
        reason: null,
        response: null,
        sponsor: null,
        approved: null,
        created: null,
        isChecked: false,
        needsEditing: null,
        is_existing_account: null

      }
    };
    const spyOnEmailMatches = spyOn(component, 'emailMatchesAccount').and.returnValue(true);
    component.setNeedsEditing({
      id: 1, organization: 1, response: 1, sponsor: 1, reason: 1,
      is_existing_account: true, username_valid: false
    })
    expect(component.accountsListProps[1].needsEditing).toBeFalse();
  })
});
