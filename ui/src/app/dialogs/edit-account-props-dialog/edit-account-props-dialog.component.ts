import {Component, Inject, OnInit} from '@angular/core';
import {AbstractControl, UntypedFormControl, UntypedFormGroup, ValidationErrors, Validators} from '@angular/forms';
import {
  MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA,
  MatLegacyDialogRef as MatDialogRef
} from '@angular/material/legacy-dialog';
import {HttpClient, HttpParams} from '@angular/common/http';
import {iif, Observable, Subject} from 'rxjs';
import {finalize, map, switchMap, tap} from 'rxjs/operators';
import {UserConfig, UserConfigService} from '../../auth/user-config.service';
import {environment} from "@environments/environment";
import {Response as ServiceResponse} from "../../services/base.service"
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

function UsernameValidator(control: AbstractControl): ValidationErrors | null {
  const lastChar = control.value?.slice(-1);
  return parseInt(lastChar) ? {username: 'Username cannot end with a numerical value.'} : null;
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
  groupsLoading = false;
  // Form Group
  editAccountPropsForm: UntypedFormGroup = new UntypedFormGroup({
    username: new UntypedFormControl(null, [UsernameValidator]),
    groups: new UntypedFormControl([]),
    sponsor: new UntypedFormControl(null, [Validators.required]),
    response: new UntypedFormControl(null, [Validators.required]),
    reason: new UntypedFormControl(null, [Validators.required]),
  });

  customerFormError: string = null;

  constructor(private http: HttpClient,
              public dialogRef: MatDialogRef<EditAccountPropsDialogComponent>,
              @Inject(MAT_DIALOG_DATA) public data, private userConfig: UserConfigService) {
  }

  ngOnInit() {
    this.responses = this.http.get<Response[]>(`${environment.local_service_endpoint}/v1/responses/`, {
      params: new HttpParams().set('for_approver', 'true')
    });
    this.getSponsors();
    this.editAccountPropsForm.controls.groups.disable();
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
          this.http.get<Sponsor>(`${environment.local_service_endpoint}/v1/sponsors/${config.id}/`).pipe(map(s => [s])),
          this.http.get<Sponsor[]>(`${environment.local_service_endpoint}/v1/sponsors/`,
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
      this.http.get<ServiceResponse>(`${environment.local_service_endpoint}/v1/agol/groups/`,
        {params: new HttpParams().set('response', response.toString())}).pipe(
        tap((res) => {
          this.groups.next(res.results);
        }),
        finalize(() => this.editAccountPropsForm.controls.groups.enable())
      ).subscribe();
    }
  }

}
