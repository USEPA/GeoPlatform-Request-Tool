import {Component, OnInit} from '@angular/core';
import {BaseService} from '../services/base.service';
import {HttpClient} from '@angular/common/http';
import {LoadingService} from '../services/loading.service';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import {Observable} from 'rxjs';
import {RequestFieldCoordDialogComponent} from '../dialogs/request-field-coord-dialog/request-field-coord-dialog.component';
import {LoginService} from '../services/login.service';

export interface FieldCoordinator {
  first_name: string;
  last_name: string;
  phone_number: number;
  email: string;
  region: string;
}

@Component({
  selector: 'field-coord-list',
  templateUrl: './field-coord-list.component.html',
  styleUrls: ['./field-coord-list.component.css']
})
export class FieldCoordListComponent implements OnInit {
  accounts: BaseService;
  displayedColumns = ['first_name', 'last_name', 'email', 'region'];
  groups: Observable<[]>;
  field_coordinator: FieldCoordinator;

  constructor(public http: HttpClient, loadingService: LoadingService, public snackBar: MatSnackBar,
              public dialog: MatDialog, public loginService: LoginService) {
    this.accounts = new BaseService('v1/account/approvals/', http, loadingService);
  }

  ngOnInit() {
    // this.accounts.getItems().subscribe();
  }

  openRequestFieldCoordDialog(): void {
    const dialogRef = this.dialog.open(RequestFieldCoordDialogComponent, {
      width: '800px',
      data: {
        first_name: null,
        last_name: null,
        phone_number: null,
        email: null,
        region: null,
        agol_user: null,
        emergency_response: null
      }
    });

    dialogRef.afterClosed().subscribe(formInputValues => {
      if (formInputValues) {
        this.field_coordinator = formInputValues;
        this.emailFieldCoordRequest();
      }
    });
  }

  async emailFieldCoordRequest() {
    const result = await this.http.post('/v1/email_field_coordinator_request/', this.field_coordinator).toPromise();
    if (result === true) {
      this.snackBar.open('Email sent', null, {duration: 2000});
    }
  }

}
