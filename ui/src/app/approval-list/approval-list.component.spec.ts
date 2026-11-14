import { beforeEach, describe, expect, it, vi } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

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
        return { afterClosed: () => of({ confirmed: true }) };
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

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [ApprovalListComponent, FilterInputComponent],
            imports: [CustomMaterialModule, FormsModule, ReactiveFormsModule, CdkTableModule],
            providers: [
                { provide: MatDialog, useClass: MatDialogMock },
                { provide: LoadingService, useValue: { setLoading: () => null } },
                { provide: LoginService, useValue: {} },
                { provide: MatSnackBar, useClass: MatSnackBarStub },
                provideHttpClient(withXhr(), withInterceptorsFromDi()),
                provideHttpClientTesting()
            ]
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(ApprovalListComponent);
        component = fixture.componentInstance;
        matSnackBar = TestBed.inject(MatSnackBar);
        httpTestingController = TestBed.inject(HttpTestingController);

        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should handle a cleared user config on logout', () => {
        component.UserConfigService.clearConfig();
        fixture.detectChanges();

        expect(component.userConfig).toBeNull();
        expect(component.getEmailMismatchTooltip(component.userConfig)).toBe('');
        const openDialog = vi.spyOn(component.dialog, 'open');
        const notify = vi.spyOn(matSnackBar, 'open');

        component.openApproveOptions();

        expect(openDialog).not.toHaveBeenCalled();
        expect(notify).toHaveBeenCalledWith('Please log in before approving requests.', 'Dismiss');
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
    });it('should notify users of successful approval', () => {
        vi.spyOn(matSnackBar, 'open').mockReturnValue({} as any);
        vi.spyOn(component.accounts, 'getItems').mockReturnValue(of([{}]));
        component.selectedAccountIds = [1];
        component.createAccounts();
        const req = httpTestingController.expectOne('/api/v1/account/approvals/approve/');
        req.flush({});
        expect(matSnackBar.open).toHaveBeenCalledWith('Success!', '', { duration: 6000, panelClass: ['snackbar-success'] });
    });

    it('should notify users of error if returned from server', () => {
        vi.spyOn(matSnackBar, 'open').mockReturnValue({} as any);
        vi.spyOn(component.accounts, 'getItems').mockReturnValue(of([{}]));
        component.selectedAccountIds = [1];
        component.createAccounts();
        const req = httpTestingController.expectOne('/api/v1/account/approvals/approve/');
        const errorResponse = new HttpErrorResponse({ error: 'error', status: 403 });
        req.flush('', errorResponse);
        expect(matSnackBar.open).toHaveBeenCalledWith('Http failure response for /api/v1/account/approvals/approve/: 403 Unknown Error', '', {
            duration: 6000,
            panelClass: ['snackbar-error']
        });
    });

    it('should notify users of successful approval update with group as property', () => {
        vi.spyOn(matSnackBar, 'open').mockReturnValue({} as any);
        vi.spyOn(component, 'setNeedsEditing').mockImplementation((param) => {
            expect(param).toBe(updateApprovalTest);
        });
        component.updateRecord(updateApprovalTest).subscribe();
        const url = `/api/v1/account/approvals/${updateApprovalTest.id}/`;
        const req = httpTestingController.expectOne(url);
        expect(req.request.method).toBe('PUT');
        req.flush(updateApprovalTest);
        expect(matSnackBar.open).toHaveBeenCalledWith('Success', '', Object({ duration: 2000 }));
    });

    it('should set needs editing if missing required fields', () => {
        component.accountsListProps = { 1: createAccountProps() };
        component.setNeedsEditing({ id: 1, organization: null });
        expect(component.accountsListProps[1].needsEditing).toBeTruthy();

    });

    it('should mark needs editing true if is existing account and email does not match', () => {
        component.accountsListProps = { 1: createAccountProps() };
        const spyOnEmailMatches = vi.spyOn(component, 'emailMatchesAccount').mockReturnValue(false);
        component.setNeedsEditing({
            id: 1, organization: 1, response: 1, sponsor: 1, reason: 1,
            is_existing_account: true, username_valid: false, denied: null
        });
        expect(component.accountsListProps[1].needsEditing).toBeTruthy();
    });
    it('should mark needs editing false if is existing account and email does match', () => {
        component.accountsListProps = { 1: createAccountProps() };
        const spyOnEmailMatches = vi.spyOn(component, 'emailMatchesAccount').mockReturnValue(true);
        component.setNeedsEditing({
            id: 1, organization: 1, response: 1, sponsor: 1, reason: 1,
            is_existing_account: true, username_valid: false, denied: null
        });
        expect(component.accountsListProps[1].needsEditing).toBe(false);
    });

    it('should hide the denied column when denied requests are not shown', () => {
        component.accounts.filter = { is_denied: false, page: 1, search: '' };
        component.displayedColumns.push('denied');

        component.handleDeniedVisibility();

        expect(component.displayedColumns).not.toContain('denied');
    });

    it('should add the denied column before delete when denied requests are shown', () => {
        component.accounts.filter = { is_denied: true, page: 1, search: '' };

        component.handleDeniedVisibility();

        expect(component.displayedColumns[component.displayedColumns.length - 2]).toBe('denied');
        expect(component.displayedColumns.filter(column => column === 'denied').length).toBe(1);
    });

    it('should not add the denied column more than once', () => {
        component.accounts.filter = { is_denied: true, page: 1, search: '' };
        component.displayedColumns.splice(-1, 0, 'denied');

        component.handleDeniedVisibility();

        expect(component.displayedColumns.filter(column => column === 'denied').length).toBe(1);
    });

    it('should deny selected requests after confirmation and refresh the list', () => {
        const dialogOpen = vi.spyOn(component.dialog, 'open').mockReturnValue({
            afterClosed: () => of(true)
        } as any);
        vi.spyOn(component.accounts, 'getItems').mockReturnValue(of([]));
        const setAccountsListProps = vi.spyOn(component, 'setAccountsListProps').mockReturnValue(undefined);
        const clearAllSelected = vi.spyOn(component, 'clearAllSelected').mockReturnValue(undefined);
        vi.spyOn(matSnackBar, 'open').mockReturnValue({} as any);
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
                    'Confirm you want to deny the selected requests'
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
        vi.spyOn(component.dialog, 'open').mockReturnValue({
            afterClosed: () => of(false)
        } as any);
        component.accountsListProps = { 1: createAccountProps() };
        component.selectedAccountIds = [1];

        component.denyRequests();

        httpTestingController.expectNone('/api/v1/account/approvals/deny/');
    });
});
