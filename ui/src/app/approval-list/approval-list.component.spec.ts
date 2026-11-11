import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import { AccountProps, ApprovalListComponent } from './approval-list.component';
import { of } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { HttpClient, HttpErrorResponse, provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { LoadingService } from '@services/loading.service';
import { LoginService } from '../auth/login.service';
import { MatSnackBar } from '@angular/material/snack-bar';

import { UpdateApprovalTest } from './approval-list-mock-data';
import { FilterInputComponent } from '../filter-input/filter-input.component';
import { CustomMaterialModule } from '../core/material.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CdkTableModule } from '@angular/cdk/table';
import { GenericConfirmDialogComponent } from '../dialogs/generic-confirm-dialog/generic-confirm-dialog.component';

const updateApprovalTest = new UpdateApprovalTest();

function createAccountProps(): AccountProps {
    return {
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        groups: [],
        organization: '',
        reason: '',
        response: null,
        sponsor: 0,
        approved: '',
        created: '',
        denied: null,
        isChecked: false,
        needsEditing: null,
        is_existing_account: null
    };
}

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

  describe('Deny button visibility', () => {
        beforeEach(() => {
            component.accountsListProps = {
                1: createAccountProps(),
                2: { ...createAccountProps(), created: '2026-11-10T12:00:00Z' }
            };
        });

        it('should hide Deny when no request is selected', () => {
            fixture.detectChanges();

            expect(fixture.nativeElement.querySelector('#denyBtn')).toBeNull();
        });

        it('should show Deny when only uncreated requests are selected', () => {
            component.accountsListProps[3] = createAccountProps();
            component.updateSelectedAccount({ checked: true, source: { value: 1 } });
            component.updateSelectedAccount({ checked: true, source: { value: 3 } });
            fixture.detectChanges();

            expect(fixture.nativeElement.querySelector('#denyBtn')).not.toBeNull();
        });

        it('should hide Deny when a created request is selected', () => {
            component.updateSelectedAccount({ checked: true, source: { value: 2 } });
            fixture.detectChanges();

            expect(fixture.nativeElement.querySelector('#denyBtn')).toBeNull();
        });

        it('should hide Deny when select all includes a created request', () => {
            component.updateSelectedAccount({ checked: true }, true);
            fixture.detectChanges();

            expect(component.selectedAccountIds).toEqual([1, 2]);
            expect(fixture.nativeElement.querySelector('#denyBtn')).toBeNull();
        });

        it('should show Deny again when the created request is deselected', () => {
            component.updateSelectedAccount({ checked: true }, true);
            component.updateSelectedAccount({ checked: false, source: { value: 2 } });
            fixture.detectChanges();

            expect(fixture.nativeElement.querySelector('#denyBtn')).not.toBeNull();
        });

        it('should hide Deny after clearing the selection', () => {
            component.updateSelectedAccount({ checked: true, source: { value: 1 } });
            component.clearAllSelected();
            fixture.detectChanges();

            expect(fixture.nativeElement.querySelector('#denyBtn')).toBeNull();
        });
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
      'Http failure response for /api/v1/account/approvals/approve/: 403 Unknown Error', null, {
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
      is_existing_account: true, username_valid: false, denied: null
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
      is_existing_account: true, username_valid: false, denied: null
    })
    expect(component.accountsListProps[1].needsEditing).toBeFalse();
  })

  it('should hide the denied column when denied requests are not shown', () => {
    component.accounts.filter = {is_denied: false};
    component.displayedColumns.push('denied');

    component.handleDeniedVisibility();

    expect(component.displayedColumns).not.toContain('denied');
  });

  it('should add the denied column before delete when denied requests are shown', () => {
    component.accounts.filter = {is_denied: true};

    component.handleDeniedVisibility();

    expect(component.displayedColumns[component.displayedColumns.length - 2]).toBe('denied');
    expect(component.displayedColumns.filter(column => column === 'denied').length).toBe(1);
  });

  it('should not add the denied column more than once', () => {
    component.accounts.filter = {is_denied: true};
    component.displayedColumns.splice(-1, 0, 'denied');

    component.handleDeniedVisibility();

    expect(component.displayedColumns.filter(column => column === 'denied').length).toBe(1);
  });

  it('should deny selected requests after confirmation and refresh the list', () => {
    const dialogOpen = spyOn(component.dialog, 'open').and.returnValue({
      afterClosed: () => of(true)
    } as any);
    spyOn(component.accounts, 'getItems').and.returnValue(of([]));
    const setAccountsListProps = spyOn(component, 'setAccountsListProps');
    const clearAllSelected = spyOn(component, 'clearAllSelected');
    spyOn(matSnackBar, 'open');
    component.accountsListProps = {
            1: { ...createAccountProps(), first_name: 'First', last_name: 'Requestor' },
            2: { ...createAccountProps(), first_name: 'Second', last_name: 'Requestor' }
        };
        component.selectedAccountIds = [1, 2];

    component.denyRequests();

        expect(dialogOpen).toHaveBeenCalledWith(GenericConfirmDialogComponent, {
            width: '500px',
            data: {
                message: expect.stringMatching(
                    /^\s*Confirm you want to deny the selected requests for:<br\/>\s*<b>First Requestor<br\/>Second Requestor<\/b>\s*$/
                )
            }
        });
        const req = httpTestingController.expectOne('/api/v1/account/approvals/deny/');
        expect(req.request.method).toBe('POST');
        expect(req.request.body).toEqual({ ids: [1, 2] });
        req.flush({});

    expect(setAccountsListProps).toHaveBeenCalledWith([]);
    expect(clearAllSelected).toHaveBeenCalled();
    expect(matSnackBar.open).toHaveBeenCalledWith('Success');
  });

  it('should not deny selected requests when confirmation is declined', () => {
    spyOn(component.dialog, 'open').and.returnValue({
      afterClosed: () => of(false)
    } as any);
    component.accountsListProps = { 1: createAccountProps() };
        component.selectedAccountIds = [1];

    component.denyRequests();

    httpTestingController.expectNone('/api/v1/account/approvals/deny/');
  });
});
