import {Component, Inject, OnInit} from '@angular/core';
import {UntypedFormControl, UntypedFormGroup, Validators} from '@angular/forms';
import {MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA, MatLegacyDialogRef as MatDialogRef} from '@angular/material/legacy-dialog';
import {HttpClient, HttpParams} from '@angular/common/http';
import {ReplaySubject} from 'rxjs';
import {map, tap} from 'rxjs/operators';

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
  requestFieldCoordForm: UntypedFormGroup = new UntypedFormGroup({
    first_name: new UntypedFormControl(null, [Validators.required]),
    last_name: new UntypedFormControl(null, [Validators.required]),
    phone_number: new UntypedFormControl(null, [Validators.required,
      Validators.pattern('[2-9]\\d{9}')]),
    email: new UntypedFormControl(null, [Validators.required, Validators.email]),
    agol_user: new UntypedFormControl(null, [Validators.required]),
    emergency_response: new UntypedFormControl(null)
  });

  constructor(public dialogRef: MatDialogRef<RequestFieldCoordDialogComponent>,
              public http: HttpClient, public loadingService: LoadingService,
              @Inject(MAT_DIALOG_DATA) public data: FieldCoordinator) {
  }

  ngOnInit() {
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
