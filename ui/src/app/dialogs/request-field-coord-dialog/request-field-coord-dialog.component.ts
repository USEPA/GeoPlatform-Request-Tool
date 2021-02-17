import {Component, Inject, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {HttpClient} from '@angular/common/http';
import {ReplaySubject} from 'rxjs';
import {map} from 'rxjs/operators';

import {BaseService} from '@services/base.service';
import {FieldCoordinator} from '../../field-coord-list/field-coord-list.component';
import {LoadingService} from '@services/loading.service';
import {AgolGroup} from '../edit-account-props-dialog/edit-account-props-dialog.component';



@Component({
  selector: 'app-request-field-coord-dialog',
  templateUrl: './request-field-coord-dialog.component.html',
  styleUrls: ['./request-field-coord-dialog.component.css']
})
export class RequestFieldCoordDialogComponent implements OnInit {
  groupsService: BaseService;
  authGroupChoices: ReplaySubject<AgolGroup[]> = new ReplaySubject<AgolGroup[]>();
  requestFieldCoordForm: FormGroup = new FormGroup({
    first_name: new FormControl(null, [Validators.required]),
    last_name: new FormControl(null, [Validators.required]),
    phone_number: new FormControl(null, [Validators.required,
      Validators.pattern('[2-9]\\d{9}')]),
    email: new FormControl(null, [Validators.required, Validators.email]),
    authoritative_group: new FormControl(null, [Validators.required]),
    agol_user: new FormControl(null, [Validators.required]),
    emergency_response: new FormControl(null)
  });

  constructor(public dialogRef: MatDialogRef<RequestFieldCoordDialogComponent>,
              public http: HttpClient, public loadingService: LoadingService,
              @Inject(MAT_DIALOG_DATA) public data: FieldCoordinator) {
    this.groupsService = new BaseService('v1/agol/groups', this.http, this.loadingService);
  }

  async ngOnInit() {
    await this.groupsService.getList<AgolGroup>({is_auth_group: true}).pipe(
      map((response) => {
        this.authGroupChoices.next(response.results);
      })
    ).toPromise();
  }

  submit() {
    this.dialogRef.close({result: this.requestFieldCoordForm.value});
    this.requestFieldCoordForm.reset();
  }

  dismiss() {
    this.dialogRef.close(null);
    this.requestFieldCoordForm.reset();
  }

}
