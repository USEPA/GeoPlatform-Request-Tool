import {Component, Inject, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {HttpClient, HttpParams} from '@angular/common/http';
import {iif, Observable, Subject} from 'rxjs';
import {map, switchMap, tap} from 'rxjs/operators';
import {UserConfig, UserConfigService} from '../../auth/user-config.service';

export interface AgolGroup {
  id: number;
  title: string;
}

export interface Response {
  id: number;
  name: string;
}

export interface Sponsor {
  id: number;
  first_name: string;
  last_name: string;
}

@Component({
  selector: 'app-edit-account-props-dialog',
  templateUrl: './edit-account-props-dialog.component.html',
  styleUrls: ['./edit-account-props-dialog.component.css']
})
export class EditAccountPropsDialogComponent implements OnInit {
  groups: Subject<AgolGroup[]> = new Subject<AgolGroup[]>();
  responses: Observable<Response[]>;
  sponsors: Subject<Sponsor[]> = new Subject<Sponsor[]>();
  current_user: Observable<UserConfig>;
  // Form Group
  editAccountPropsForm: FormGroup = new FormGroup({
    username: new FormControl(null),
    groups: new FormControl([]),
    sponsor: new FormControl(null, [Validators.required]),
    response: new FormControl(null, [Validators.required]),
    reason: new FormControl(null, [Validators.required]),
  });
  customerFormError: string = null;

  constructor(private http: HttpClient,
              public dialogRef: MatDialogRef<EditAccountPropsDialogComponent>,
              @Inject(MAT_DIALOG_DATA) public data, private userConfig: UserConfigService) {
  }

  async ngOnInit() {
    this.responses = this.http.get<Response[]>('/v1/responses/', {
      params: new HttpParams().set('for_approver', 'true')});
    this.getSponsors();
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

  getSponsors() {
    this.userConfig.config.pipe(
      switchMap(config => {
        return iif(() => config.is_sponsor,
          this.http.get<Sponsor>(`/v1/sponsors/${config.id}`).pipe(map(s => [s])),
          this.http.get<Sponsor[]>('/v1/sponsors/',
      {params: new HttpParams().set('agol_info__delegates', config.id.toString())}).pipe(
        map(r => r['results'])
          ));
      }),
      tap(s => {
        this.sponsors.next(s);
        if (s.length === 1) {
          this.editAccountPropsForm.patchValue({sponsor: s[0].id});
        }
      })
    ).subscribe();
  }

  getGroups(response: number) {
    if (response) {
      this.http.get<AgolGroup[]>('/v1/agol/groups',
        {params: new HttpParams().set('response', response.toString())}).pipe(
        tap(r => this.groups.next(r))
      ).subscribe();
    }
  }

}
