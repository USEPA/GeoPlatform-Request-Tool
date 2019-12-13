import {Component, Inject, OnInit} from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import {FormControl, FormGroup, ValidationErrors, ValidatorFn, Validators} from '@angular/forms';


export const passwordMatchValidator: ValidatorFn = (control: FormGroup): ValidationErrors | null => {
  const password = control.get('passwordInput');
  const confirm = control.get('passwordConfirm');

  return password && confirm && password.value !== confirm.value ? {'passwordMatch': true} : null;
};

@Component({
  selector: 'app-confirm-approval-dialog',
  templateUrl: './confirm-approval-dialog.component.html',
  styleUrls: ['./confirm-approval-dialog.component.css']
})

export class ConfirmApprovalDialogComponent {
  passwordForm: FormGroup = new FormGroup({
    passwordInput: new FormControl(null,
      [Validators.required, Validators.pattern('(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d@$!%*#?&]{13,}')]
    ),
    passwordConfirm: new FormControl(null, Validators.required)
  },
    {validators: passwordMatchValidator}
  );

  constructor(public dialogRef: MatDialogRef<ConfirmApprovalDialogComponent>,
              @Inject(MAT_DIALOG_DATA) public data) { }

  confirm() {
    this.dialogRef.close({confirmed: true, password: this.passwordForm.value.passwordInput});
    this.passwordForm.reset();
  }

  dismiss() {
    this.dialogRef.close({confirmed: false, password: null});
    this.passwordForm.reset();
  }

}
