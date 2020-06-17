import {Component, OnInit} from '@angular/core';
import {BaseService} from '../services/base.service';
import {HttpClient} from '@angular/common/http';
import {LoadingService} from '../services/loading.service';
import {catchError, map, share, switchMap, tap} from 'rxjs/operators';
import {MatDialog} from '@angular/material/dialog';
import {MatSnackBar} from '@angular/material/snack-bar';
import {forkJoin, iif, Observable, of} from 'rxjs';
import {EditAccountPropsDialogComponent} from '../dialogs/edit-account-props-dialog/edit-account-props-dialog.component';
import {ConfirmApprovalDialogComponent} from '../dialogs/confirm-approval-dialog/confirm-approval-dialog.component';
import {LoginService} from '../auth/login.service';

export interface AccountProps {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  groups: [];
  organization: string;
  reason: string;
  response: number;
  sponsor: number;
  description: string;
  approved: boolean;
  created: boolean;
  isChecked: boolean;
  needsEditing: boolean;
}

export interface Accounts {
  [id: number]: AccountProps;
}

@Component({
  selector: 'app-approval-list',
  templateUrl: './approval-list.component.html',
  styleUrls: ['./approval-list.component.css']
})
export class ApprovalListComponent implements OnInit {
  accounts: BaseService;
  displayedColumns = ['selected', 'first_name', 'last_name', 'email', 'username', 'organization', 'groups', 'response',
    'sponsor', 'reason', 'description', 'approved', 'created'];
  // took out "roll" and "user_type"
  selectedAccountIds = [];
  accountsListProps: Accounts = {};
  allChecked: boolean;
  needsEditing: boolean;
  isApprovalReady: boolean;
  roles: Observable<[]>;
  user_types: Observable<[]>;

  constructor(public http: HttpClient, loadingService: LoadingService, public snackBar: MatSnackBar,
              public dialog: MatDialog, public loginService: LoginService) {
    this.accounts = new BaseService('v1/account/approvals/', http, loadingService);
  }

  async ngOnInit() {
    // this was used to give superusers full list when logging in... but they didn't like it
    // this.loginService.is_superuser ? null : this.accounts.filter = {approved_and_created: false};

    // set accounts list record properties
    // this.setAccountsListProps();

    this.accounts.filter = {created: false};
    this.accounts.getItems().pipe(
      tap(response => this.setAccountsListProps(response))
    ).subscribe();
    this.roles = this.http.get<[]>('/v1/account/approvals/roles').pipe(share());
    this.user_types = this.http.get<[]>('/v1/account/approvals/user_types').pipe(share());
  }

  setAccountsListProps(init_accounts) {
    this.needsEditing = false;
    this.isApprovalReady = false;
    // const init_accounts = await this.accounts.getItems().toPromise();
    for (const account of init_accounts) {
      const acctProps: AccountProps = {
        first_name: account.first_name,
        last_name: account.first_name,
        username: account.username,
        email: account.email,
        groups: account.groups,
        organization: account.organization,
        reason: account.reason,
        response: account.response,
        sponsor: account.sponsor,
        description: account.description,
        approved: account.approved,
        created: account.created,
        isChecked: false,
        needsEditing: null
      };
      this.accountsListProps[account.id] = acctProps;
      this.setNeedsEditing(account);
    }

    this.selectedAccountIds = [];

  }

  getSelectedAccountIds() {
    const selectedAccountIds = [];
    for (const id in this.accountsListProps) {
      if (this.accountsListProps.hasOwnProperty(id) && this.accountsListProps[id].isChecked) {
        const idNum = Number(id);
        selectedAccountIds.push(idNum);
      }
    }
    return selectedAccountIds;
  }

  getApprovalStatus() {
    let isApprovalReady = true;
    for (const id of this.selectedAccountIds) {
      if (this.accountsListProps[id].needsEditing ||
        (this.accountsListProps[id].approved && this.accountsListProps[id].created)) {
        isApprovalReady = false;
      }
    }
    return isApprovalReady;
  }

  updateSelectedAccount(event, all = false) {
    let needsEditing = false;
    this.isApprovalReady = false;
    for (const id in this.accountsListProps) {
      if (this.accountsListProps.hasOwnProperty(id)) {
        if (all) {
          this.accountsListProps[id].isChecked = event.checked;
          this.allChecked = event.checked;
        } else {
          const evtId = event.source.value.toString();
          this.accountsListProps[evtId].isChecked = event.checked;
          if (!event.checked) {
            this.allChecked = event.checked;
          }
        }
        if (this.accountsListProps[id].isChecked) {
          if (this.accountsListProps[id].needsEditing) {
            needsEditing = true;
          }
        }
      }
    }
    this.needsEditing = needsEditing;
    this.selectedAccountIds = this.getSelectedAccountIds();
    if (this.selectedAccountIds.length > 0) {
      this.isApprovalReady = this.getApprovalStatus();
    }
  }

  updateRecord(record) {
    return this.http.put(`/v1/account/approvals/${record.id}/`, record).pipe(
      tap(response => {
        this.setNeedsEditing(response);
        this.accounts.dataChange.next(this.accounts.data);
        this.snackBar.open('Success', null, {duration: 2000});
      }),
      catchError(() => of(this.snackBar.open('Error', null, {duration: 3000})))
    );
  }

  editAccountDialog(): void {
    let data = null;
    if (this.selectedAccountIds.length === 1) {
      data = {
        isBulkEdit: false,
        ...this.accountsListProps[this.selectedAccountIds[0]]
      };
    } else {
      const defaults: AccountProps = this.accountsListProps[this.selectedAccountIds[0]];
      for (const id of this.selectedAccountIds) {
        defaults.groups.filter(group => this.accountsListProps[id].groups.includes(group));
        defaults.response = this.accountsListProps[id].response === defaults.response ? defaults.response : null;
        defaults.reason = this.accountsListProps[id].reason === defaults.reason ? defaults.reason : '';
        defaults.description = this.accountsListProps[id].description === defaults.description ? defaults.description : '';
      }
      data = {
        isBulkEdit: true,
        groups: defaults.groups,
        response: defaults.response,
        reason: defaults.reason,
        description: defaults.description
      };
    }
    const dialogRef = this.dialog.open(EditAccountPropsDialogComponent, {
      width: '500px',
      data: data
    });

    dialogRef.afterClosed().pipe(
      switchMap(formInputValues => {
      const accountUpdates = [];
      if (formInputValues) {
        for (const id in this.accountsListProps) {
          if (this.accountsListProps[id].isChecked) {
            const updatedRecord = this.accountsListProps[id];
            updatedRecord['id'] = Number(id);
            for (const key in formInputValues) {
              if (key in updatedRecord) {
                updatedRecord[key] = formInputValues[key];
              }
            }
            accountUpdates.push(this.updateRecord(updatedRecord));
          }
        }
      }
      return forkJoin(accountUpdates);
    }),
      switchMap(() => this.accounts.getItems()),
      tap(() => this.isApprovalReady = this.getApprovalStatus())).subscribe();
  }

  confirmApproval() {
    let password_needed = false;
    for (const account of this.accounts.data) {
      if (this.selectedAccountIds.indexOf(account.id) > -1 && account.username_valid) {
        password_needed = true;
        break;
      }
    }
    const dialogRef = this.dialog.open(ConfirmApprovalDialogComponent, {
      width: '400px',
      data: {
        password_needed: password_needed
      }
    });
    dialogRef.afterClosed().pipe(switchMap(results => {
        return iif(() => results.confirmed, this.http.post('/v1/account/approvals/approve/',
          {accounts: this.selectedAccountIds, password: results.password}).pipe(
          switchMap(response => iif(() => response !== undefined, this.accounts.getItems().pipe(tap(() => {

            this.snackBar.open('Success', null, {duration: 2000});
            // clear selected accounts after approval issue #33
            this.selectedAccountIds.length = 0;
          }))))
          )
        );
      }),
      catchError(() => of(this.snackBar.open('Error', null, {duration: 3000})))
    ).subscribe();
  }

  setNeedsEditing(account) {
    let needsEditing = false;
    // removed group as requirement for editing per issue #31
    if (!account.organization || !account.response || !account.sponsor || !account.reason || !account.description) {
      needsEditing = true;
    }
    this.accountsListProps[account.id].needsEditing = needsEditing;
  }

}
