import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {BehaviorSubject, Observable, of} from 'rxjs';
import {catchError, finalize, map, share, tap} from 'rxjs/operators';
import {MatLegacySnackBar as MatSnackBar} from '@angular/material/legacy-snack-bar';
import {environment} from '../../environments/environment';
import {ActivatedRoute} from '@angular/router';

interface Response {
  id: number;
  name: string;
}

@Component({
  selector: 'app-request-form',
  templateUrl: './request-form.component.html',
  styleUrls: ['./request-form.component.css']
})
export class RequestFormComponent implements OnInit {
  submitting: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  responses: Observable<Response[]>;
  requestForm: FormGroup = new FormGroup({
    first_name: new FormControl(null, Validators.required),
    last_name: new FormControl(null, Validators.required),
    email: new FormControl(null, [Validators.required, Validators.email]),
    organization: new FormControl(null, Validators.required),
    response: new FormControl(null, Validators.required),
    recaptcha: new FormControl(null, Validators.required)
  });

  constructor(public http: HttpClient, public matSnackBar: MatSnackBar, private activatedRoute: ActivatedRoute) {
  }

  ngOnInit() {
    const queryParams = this.activatedRoute.snapshot.queryParamMap;
    const params = {
      is_disabled: false,
      id_in: queryParams.has('response') ? queryParams.get('response') : ''
    };
    this.responses = this.http.get<Response[]>(
      `${environment.local_service_endpoint}/v1/responses/`,
      {params}
    ).pipe(
      tap(r => {
        if (r.length === 1) {
          this.requestForm.patchValue({response: r[0].id});
        }
      })
    );
  }

  submit() {
    this.matSnackBar.dismiss();
    this.submitting.next(true);
    this.http.post(`${environment.local_service_endpoint}/v1/account/request/`, this.requestForm.value).pipe(
      tap(response => {
        this.matSnackBar.open('Request has been successfully submitted', 'Dismiss', {
          panelClass: ['snackbar-success'],
          verticalPosition: 'top'
        });
        this.requestForm.reset();
      }),
      finalize(() => this.submitting.next(false)),
      catchError(e => {
        const message = e.error.details ? e.error.details.join(', ') : 'Error';
        return of(this.matSnackBar.open(message, 'Dismiss', {
          verticalPosition: 'top',
          // duration: 8000,
          panelClass: ['snackbar-error']
        }));
      })
    ).subscribe();
  }

}
