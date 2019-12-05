import {Component, Inject, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {FieldCoordinator} from '../../field-coord-list/field-coord-list.component';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';


@Component({
  selector: 'app-request-field-coord-dialog',
  templateUrl: './request-field-coord-dialog.component.html',
  styleUrls: ['./request-field-coord-dialog.component.css']
})
export class RequestFieldCoordDialogComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<RequestFieldCoordDialogComponent>,
              @Inject(MAT_DIALOG_DATA) public data: FieldCoordinator) { }

  requestFieldCoordForm: FormGroup;

  ngOnInit() {
    // Form Group
    this.requestFieldCoordForm = new FormGroup({
      first_name: new FormControl(null, [Validators.required]),
      last_name: new FormControl(null, [Validators.required]),
      phone_number: new FormControl(null, [Validators.required,
        Validators.pattern('[6-9]\\d{9}')]),
      email: new FormControl(null, [Validators.required, Validators.email]),
      region: new FormControl(null, [Validators.required]),
      agol_user: new FormControl(null, [Validators.required]),
      emergency_response: new FormControl(null)
    });
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
