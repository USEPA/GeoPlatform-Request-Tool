import {Component, Inject, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {HttpClient} from '@angular/common/http';

export interface AgolGroup {
  id: number;
  title: string;
}
export interface Sponsor {
  value: number;
  display: string;
}

@Component({
  selector: 'app-edit-account-props-dialog',
  templateUrl: './edit-account-props-dialog.component.html',
  styleUrls: ['./edit-account-props-dialog.component.css']
})
export class EditAccountPropsDialogComponent implements OnInit {
  groups: AgolGroup[];
  sponsors: Sponsor[];
  // Form Group
  editAccountPropsForm: FormGroup = new FormGroup({
    username: new FormControl(null),
    groups: new FormControl([]),
    sponsor: new FormControl(null, [Validators.required]),
    reason: new FormControl(null, [Validators.required]),
    description: new FormControl(null, [Validators.required]),
  });
  customerFormError: string = null;

  constructor(private http: HttpClient,
              public dialogRef: MatDialogRef<EditAccountPropsDialogComponent>,
              @Inject(MAT_DIALOG_DATA) public data) { }

  async ngOnInit() {
    this.groups = await this.http.get<AgolGroup[]>('/v1/agol/groups').toPromise();
    this.sponsors = await this.http.get<Sponsor[]>('/v1/account/approvals/sponsors/').toPromise();
  }

  submit() {
    if (this.data.isBulkEdit) {
      delete this.editAccountPropsForm.value.username;
    } else if (!this.data.isBulkEdit && !this.editAccountPropsForm.value.username) {
      this.customerFormError = 'Username is required.';
      return;
    }
    this.dialogRef.close(this.editAccountPropsForm.value);
    this.editAccountPropsForm.reset();
  }

  dismiss() {
    this.dialogRef.close(null);
    this.editAccountPropsForm.reset();
  }

}
