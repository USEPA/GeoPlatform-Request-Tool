import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {HttpClient} from '@angular/common/http';
import {BehaviorSubject, Observable, of} from 'rxjs';
import {catchError, finalize, map, share, tap} from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';
import {environment} from '../../environments/environment';

interface Sponsor {
  display: string;
  value: string;
}

@Component({
  selector: 'app-request-form',
  templateUrl: './request-form.component.html',
  styleUrls: ['./request-form.component.css']
})
export class RequestFormComponent implements OnInit {
  submitting: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  sponsors: Observable<Sponsor[]>;
  requestForm: FormGroup = new FormGroup({
    first_name: new FormControl(null, Validators.required),
    last_name: new FormControl(null, Validators.required),
    email: new FormControl(null, [Validators.required, Validators.email]),
    organization: new FormControl(null, Validators.required),
    sponsor: new FormControl(null, Validators.required),
    reason: new FormControl('Emergency Response', [Validators.required]),
    description: new FormControl(null),
    recaptcha: new FormControl(null, Validators.required)
  });

  constructor(public http: HttpClient, public matSnackBar: MatSnackBar) {
  }

  ngOnInit() {
    this.sponsors = this.http.get<Sponsor[]>(`${environment.local_service_endpoint}/v1/account/request/field_coordinators/`).pipe(
      map(response => response['results'])
    );
  }

  submit() {
    this.submitting.next(true);
    this.http.post(`${environment.local_service_endpoint}/v1/account/request/`, this.requestForm.value).pipe(
      tap(response => {
        this.matSnackBar.open('Success', null, {duration: 2000});
        this.requestForm.reset();
      }),
      finalize(() => this.submitting.next(false)),
      catchError(() => of(this.matSnackBar.open('Error', null, {duration: 2000})))
    ).subscribe();
  }

}
