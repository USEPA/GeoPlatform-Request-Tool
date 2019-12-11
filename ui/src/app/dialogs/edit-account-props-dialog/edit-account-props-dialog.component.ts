import {Component, Inject, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {HttpClient} from '@angular/common/http';
import {share} from 'rxjs/operators';
import {Observable} from 'rxjs';

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
  agol_groups: AgolGroup[];
  sponsors: Sponsor[];
    // Form Group
    editAccountPropsForm: FormGroup = new FormGroup({
      username: new FormControl(null, [Validators.required]),
      agol_groups: new FormControl(null),
      sponsor: new FormControl(null, [Validators.required]),
      reason: new FormControl(null, [Validators.required]),
      description: new FormControl(null, [Validators.required]),
    });

  constructor(private http: HttpClient,
              public dialogRef: MatDialogRef<EditAccountPropsDialogComponent>,
              @Inject(MAT_DIALOG_DATA) public data) { }

  async ngOnInit() {
    this.agol_groups = await this.http.get<AgolGroup[]>('/v1/agol/groups').toPromise();
    this.sponsors = await this.http.get<Sponsor[]>('/v1/account/approvals/sponsors/').toPromise();
  }

  submit() {
    this.dialogRef.close(this.editAccountPropsForm.value);
    this.editAccountPropsForm.reset();
  }

  dismiss() {
    this.dialogRef.close(null);
    this.editAccountPropsForm.reset();
  }

}
