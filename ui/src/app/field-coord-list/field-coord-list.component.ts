import {Component, OnInit} from '@angular/core';
import {BaseService} from '../services/base.service';
import {HttpClient} from '@angular/common/http';
import {LoadingService} from '../services/loading.service';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { MatLegacySnackBar as MatSnackBar } from '@angular/material/legacy-snack-bar';
import {Observable} from 'rxjs';
import {RequestFieldCoordDialogComponent} from '../dialogs/request-field-coord-dialog/request-field-coord-dialog.component';
import {LoginService} from '../auth/login.service';
import {UntypedFormControl} from "@angular/forms";
import {debounceTime, skip, startWith, tap} from "rxjs/operators";
import {environment} from "@environments/environment";

export interface FieldCoordinator {
  value: number;
  first_name: string;
  last_name: string;
  display: string;
  username: string;
  phone_number: number;
  email: string;
  authoritative_group: string;
  region: string;
  id: number;
  title: string;
}

@Component({
  selector: 'app-field-coord-list',
  templateUrl: './field-coord-list.component.html',
  styleUrls: ['./field-coord-list.component.css']
})
export class FieldCoordListComponent implements OnInit {
  sponsors: BaseService;
  // sponsors: Observable<[]>;
  displayedColumns = ['first_name', 'last_name', 'email', 'phone_number'];
  field_coordinator: FieldCoordinator;
  searchInput = new UntypedFormControl(null);

  constructor(public http: HttpClient, loadingService: LoadingService, public snackBar: MatSnackBar,
              public dialog: MatDialog, public loginService: LoginService) {
    this.sponsors = new BaseService('v1/sponsors', http, loadingService);
  }

  ngOnInit() {
    // this.sponsors.filter = {approved_and_created: true};
    this.sponsors.getItems().subscribe();

    this.searchInput.valueChanges.pipe(
      startWith(this.searchInput.value),
      skip(1),
      debounceTime(300),
      tap(searchInput => this.search(searchInput))
    ).subscribe();
  }

  search(search: any) {
    this.sponsors.filter.search = search;
    return this.sponsors.runSearch();
  }

  openRequestFieldCoordDialog(): void {
    const dialogRef = this.dialog.open(RequestFieldCoordDialogComponent, {
      width: '800px',
      data: {
        first_name: null,
        last_name: null,
        phone_number: null,
        email: null,
        authoritative_group: null,
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
      const result = await this.http.post(`${environment.local_service_endpoint}/v1/email_field_coordinator_request/`, this.field_coordinator).toPromise();
    if (result === true) {
      this.snackBar.open('Email sent', null, {duration: 2000});
    } else {
      this.snackBar.open('Email failed. Try again later.', null, {duration: 2000});
    }
  }

}
