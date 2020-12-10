import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {BehaviorSubject, Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {MatSnackBar} from '@angular/material/snack-bar';
import {map} from 'rxjs/operators';

import {Response} from '@services/base.service';
import {FieldCoordinator} from '../field-coord-list/field-coord-list.component';
import {CONFIG_SETTINGS} from '../config_settings';


@Component({
  selector: 'app-field-coord-er-request-form',
  templateUrl: './field-coord-er-request-form.component.html',
  styleUrls: ['./field-coord-er-request-form.component.css']
})
export class FieldCoordErRequestFormComponent implements OnInit {
  isLoading: Boolean;
  field_coordinators: Observable<FieldCoordinator[]>;
  tags = [];
  submitting: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(null);
  fieldTeamCoordErForm: FormGroup = new FormGroup({
    emergency_response_name: new FormControl(null, Validators.required),
    field_team_coordinators: new FormControl(null, Validators.required),
    geoplatform_groups: new FormControl(null, Validators.required),
    requester: new FormControl(null, Validators.required),
    requester_phone_number: new FormControl(null,
      [Validators.required, Validators.pattern('[2-9]\\d{9}')])
  });

  constructor(public http: HttpClient, public matSnackBar: MatSnackBar) {
    this.isLoading = true;
  }

  async ngOnInit() {
    this.field_coordinators = this.http.get<Response>('/v1/sponsors/').pipe(
      map(response => response.results)
    );
  }

  async submit() {
    this.submitting.next(true);
    const result = await this.http.post('/v1/email_field_coordinator_request/', this.fieldTeamCoordErForm.value).toPromise();
    if (result === true) {
      this.matSnackBar.open('Email sent', null, {
        duration: CONFIG_SETTINGS.snackbar_duration
      });
    } else {
      this.matSnackBar.open('Email failed. Try again later.', null, {
        duration: CONFIG_SETTINGS.snackbar_duration
      });
    }
    this.submitting.next(false);
    this.fieldTeamCoordErForm.reset();
    this.tags = [];
  }

}
