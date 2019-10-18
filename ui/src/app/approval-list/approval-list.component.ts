import {Component, OnInit} from '@angular/core';
import {BaseService} from '../services/base.service';
import {HttpClient} from '@angular/common/http';
import {LoadingService} from '../services/loading.service';
import {catchError, map, share, switchMap, tap} from 'rxjs/operators';
import {MatDialog, MatSnackBar} from '@angular/material';
import {iif, Observable, of} from 'rxjs';
import {ConfirmApprovalDialogComponent} from '../confirm-approval-dialog/confirm-approval-dialog.component';
import {LoginService} from '../services/login.service';

@Component({
  selector: 'app-approval-list',
  templateUrl: './approval-list.component.html',
  styleUrls: ['./approval-list.component.css']
})
export class ApprovalListComponent implements OnInit {
  accounts: BaseService;
  displayedColumns = ['selected', 'first_name', 'last_name', 'email', 'username', 'organization',
    'groups', 'sponsor', 'approved', 'created', 'save'];
  //took out "roll" and "user_type"
  selectedAccounts = [];
  roles: Observable<[]>;
  user_types: Observable<[]>;
  groups: Observable<[]>;
  sponsors: Observable<[]>;

  constructor(public http: HttpClient, loadingService: LoadingService, public snackBar: MatSnackBar,
              public dialog: MatDialog, public loginService: LoginService) {
    this.accounts = new BaseService('v1/account/approvals/', http, loadingService);
  }

  ngOnInit() {
    // this was used to give superusers full list when logging in... but they didn't like it
    // this.loginService.is_superuser ? null : this.accounts.filter = {approved_and_created: false};
    this.accounts.filter = {approved_and_created: false};
    this.accounts.getItems().subscribe();
    this.roles = this.http.get<[]>('/v1/account/approvals/roles').pipe(share());
    this.user_types = this.http.get<[]>('/v1/account/approvals/user_types').pipe(share());
    this.groups = this.http.get<[]>('/v1/agol/groups').pipe(share());
    this.sponsors = this.http.get<[]>('/v1/account/request/sponsors').pipe(share());
  }

  updateSelectedAccount(event, all = false) {
    if (!all) {
      const current_index = this.selectedAccounts.indexOf(event.source.value);
      if (event.checked && current_index === -1) this.selectedAccounts.push(event.source.value);
      else if (!event.checked && current_index > -1) this.selectedAccounts.splice(current_index, 1);
    } else {
      this.selectedAccounts.length = 0;
      if (event.checked) {
        for (let account of this.accounts.data) {
          this.selectedAccounts.push(account.id);
        }
      }
    }
  }

  updateRecord(record) {
    this.http.put(`/v1/account/approvals/${record.id}/`, record).pipe(
      tap(response => {
        const index = this.accounts.data.indexOf(record);
        this.accounts.data.splice(index, 1, response);
        this.accounts.dataChange.next(this.accounts.data);
        this.snackBar.open("Success", null, {duration: 2000})
      }),
      catchError(() => of(this.snackBar.open("Error", null, {duration: 3000})))
    ).subscribe();
  }

  confirmApproval() {
    let password_needed = false;
    for (let account of this.accounts.data) {
      if (this.selectedAccounts.indexOf(account.id) > -1 && account.username_valid) {
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
          {accounts: this.selectedAccounts, password: results.password}).pipe(
          switchMap(response => iif(() => response !== undefined, this.accounts.getItems().pipe(tap(() => {
            this.selectedAccounts.length = 0;
            this.snackBar.open("Success", null, {duration: 2000})
          }))))
          )
        )
      }),
      catchError(() => of(this.snackBar.open("Error", null, {duration: 3000})))
    ).subscribe();
  }

}
