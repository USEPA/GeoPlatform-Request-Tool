import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {BehaviorSubject, Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {MatSnackBar} from '@angular/material/snack-bar';
import {FieldCoordinator} from '../field-coord-list/field-coord-list.component';
import {map} from 'rxjs/operators';
import {Response} from '../services/base.service';
export interface AgolGroup {
  value: number;
  title: string;
}

@Component({
  selector: 'app-field-coord-er-request-form',
  templateUrl: './field-coord-er-request-form.component.html',
  styleUrls: ['./field-coord-er-request-form.component.css']
})
export class FieldCoordErRequestFormComponent implements OnInit {
  isLoading: Boolean;
  field_coordinators: Observable<FieldCoordinator[]>;
  agol_groups: AgolGroup[];
  submitting: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
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
    this.agol_groups = await this.http.get<AgolGroup[]>('/v1/agol/groups/all/').toPromise();
    this.field_coordinators = this.http.get<Response>('/v1/sponsors/').pipe(
      map(response => response.results)
    );
    // this.isLoading = false;
  }

  async submit() {
    this.submitting.next(true);
    const result = await this.http.post('/v1/email_field_coordinator_request/', this.fieldTeamCoordErForm.value).toPromise();
    if (result === true) {
      this.matSnackBar.open('Email sent', null, {duration: 2000});
    } else {
      this.matSnackBar.open('Email failed. Try again later.', null, {duration: 2000});
    }
    this.submitting.next(false);
    this.fieldTeamCoordErForm.reset();
  }

}
