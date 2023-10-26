import {Component, Inject, OnInit} from '@angular/core';
import { MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA, MatLegacyDialogRef as MatDialogRef } from '@angular/material/legacy-dialog';
import {UntypedFormControl, UntypedFormGroup, ValidationErrors, ValidatorFn, Validators} from '@angular/forms';
import {AccountProps} from '../../approval-list/approval-list.component';

export interface ConfirmDialogData {
  action?: string;
  password_needed?: boolean;
  selected_request?: AccountProps;
}

export const passwordMatchValidator: ValidatorFn = (control: UntypedFormGroup): ValidationErrors | null => {
  const password = control.get('passwordInput');
  const confirm = control.get('passwordConfirm');

  return password && confirm && password.value !== confirm.value ? {'passwordMatch': true} : null;
};

@Component({
  selector: 'app-confirm-approval-dialog',
  templateUrl: './confirm-approval-dialog.component.html',
  styleUrls: ['./confirm-approval-dialog.component.css']
})

export class ConfirmApprovalDialogComponent implements OnInit {
  passwordForm: UntypedFormGroup = new UntypedFormGroup({
    passwordInput: new UntypedFormControl(null,
      [Validators.required, Validators.pattern('(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d@$!%*#?&]{13,}')]
    ),
    passwordConfirm: new UntypedFormControl(null, Validators.required)
  },
    {validators: passwordMatchValidator}
  );

  constructor(public dialogRef: MatDialogRef<ConfirmApprovalDialogComponent>,
              @Inject(MAT_DIALOG_DATA) public data: ConfirmDialogData) { }

  ngOnInit() {
  }

  confirm() {
    this.dialogRef.close({confirmed: true, password: this.passwordForm.value.passwordInput});
    this.passwordForm.reset();
  }

  dismiss() {
    this.dialogRef.close({confirmed: false, password: null});
    this.passwordForm.reset();
  }

}
