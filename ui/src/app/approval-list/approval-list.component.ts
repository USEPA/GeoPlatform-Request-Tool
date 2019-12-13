import {Component, OnInit} from '@angular/core';
import {BaseService} from '../services/base.service';
import {HttpClient} from '@angular/common/http';
import {LoadingService} from '../services/loading.service';
import {catchError, map, share, switchMap, tap} from 'rxjs/operators';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import {iif, Observable, of} from 'rxjs';
import {EditAccountPropsDialogComponent} from '../dialogs/edit-account-props-dialog/edit-account-props-dialog.component';
import {ConfirmApprovalDialogComponent} from '../dialogs/confirm-approval-dialog/confirm-approval-dialog.component';
import {LoginService} from '../services/login.service';

export interface AccountProps {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  groups: [];
  organization: string;
  reason: string;
  sponsor: number;
  description: string;
  approved: boolean;
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
  displayedColumns = ['selected', 'first_name', 'last_name', 'email', 'username', 'organization', 'groups', 'sponsor',
    'reason', 'description', 'approved', 'created'];
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
    this.setAccountsListProps();

    this.accounts.filter = {approved_and_created: false};
    this.accounts.getItems().subscribe();
    this.roles = this.http.get<[]>('/v1/account/approvals/roles').pipe(share());
    this.user_types = this.http.get<[]>('/v1/account/approvals/user_types').pipe(share());
  }

  async setAccountsListProps() {
    this.needsEditing = false;
    this.isApprovalReady = false;
    const init_accounts = await this.accounts.getItems().toPromise();
    for (const account of init_accounts) {
      let needsEditing = false;
      if (!account.username || !account.email || !account.organization || !account.sponsor || account.groups.length === 0
        || !account.reason || !account.description) {
        needsEditing = true;
      }
      const acctProps: AccountProps = {
        first_name: account.first_name,
        last_name: account.first_name,
        username: account.username,
        email: account.email,
        groups: account.groups,
        organization: account.organization,
        reason: account.reason,
        sponsor: account.sponsor,
        description: account.description,
        approved: account.approved,
        isChecked: false,
        needsEditing: needsEditing
      };
      this.accountsListProps[account.id] = acctProps;
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
      if (this.accountsListProps[id].needsEditing || this.accountsListProps[id].approved) {
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
    this.http.put(`/v1/account/approvals/${record.id}/`, record).pipe(
      tap(response => {
        this.accounts.getItems().subscribe();
        this.setAccountsListProps();
        this.accounts.dataChange.next(this.accounts.data);
        this.snackBar.open('Success', null, {duration: 2000});
      }),
      catchError(() => of(this.snackBar.open('Error', null, {duration: 3000})))
    ).subscribe();
  }

  editAccountDialog(): void {
    let data = null;
    if (this.selectedAccountIds.length === 1 ) {
      data = {
        isBulkEdit: false,
        ...this.accountsListProps[this.selectedAccountIds[0]]
      };
    } else {
      data = {
        isBulkEdit: true,
        groups: [],
        sponsor: '',
        reason: '',
        description: '',
      };
    }
    const dialogRef = this.dialog.open(EditAccountPropsDialogComponent, {
      width: '500px',
      data: data
    });

    dialogRef.afterClosed().subscribe(formInputValues => {
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
            this.updateRecord(updatedRecord);
          }
        }
      }
    });
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
            this.setAccountsListProps().then( () => {
              this.snackBar.open('Success', null, {duration: 2000});
            });
          }))))
          )
        );
      }),
      catchError(() => of(this.snackBar.open('Error', null, {duration: 3000})))
    ).subscribe();
  }

}
