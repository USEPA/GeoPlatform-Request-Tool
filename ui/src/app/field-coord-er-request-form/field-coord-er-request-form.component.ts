import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {BehaviorSubject, combineLatest, forkJoin, Observable, of} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {MatSnackBar} from '@angular/material/snack-bar';
import {catchError, finalize, map, switchMap, tap} from 'rxjs/operators';

import {BaseService, Choice, Response} from '@services/base.service';
import {FieldCoordinator} from '../field-coord-list/field-coord-list.component';
import {environment} from '@environments/environment';
import {AgolGroup} from '../dialogs/edit-account-props-dialog/edit-account-props-dialog.component';
import {UserConfigService} from '../auth/user-config.service';
import {LoadingService} from '@services/loading.service';
import {AGOLRole} from '../types';


@Component({
  selector: 'app-field-coord-er-request-form',
  templateUrl: './field-coord-er-request-form.component.html',
  styleUrls: ['./field-coord-er-request-form.component.css']
})
export class FieldCoordErRequestFormComponent implements OnInit {
  @Output() saved: EventEmitter<any> = new EventEmitter<any>();
  isLoading: Boolean;
  field_coordinators: Observable<FieldCoordinator[]>;
  auth_groups: Observable<AgolGroup[]>;
  tags = [];
  submitting: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  fieldTeamCoordErForm: FormGroup = new FormGroup({
    name: new FormControl(null, Validators.required),
    users: new FormControl(null),
    assignable_groups: new FormControl(null, Validators.required),
    requester: new FormControl(null, Validators.required),
    requester_phone_number: new FormControl(null,
      [Validators.required, Validators.pattern('[2-9]\\d{9}')]),
    authoritative_group: new FormControl(null, Validators.required),
    default_reason: new FormControl(null, Validators.required),
    role: new FormControl(null, Validators.required)
  });
  responseService: BaseService;
  roleService: BaseService;
  reasons: Observable<Choice[]>;
  roles: Observable<AGOLRole[]>;

  constructor(public http: HttpClient, public matSnackBar: MatSnackBar, public userConfig: UserConfigService,
              loadingService: LoadingService) {
    this.isLoading = true;
    this.responseService = new BaseService('v1/responses', http, loadingService);
    this.roleService = new BaseService('v1/agol/roles', http, loadingService);
  }

  ngOnInit() {
    this.field_coordinators = this.http.get<Response>('/v1/sponsors/').pipe(
      map(response => response.results)
    );
    combineLatest([this.field_coordinators, this.userConfig.config]
    ).pipe(
      tap(r => {
        this.fieldTeamCoordErForm.patchValue({
          requester: r[1].id,
          requester_phone_number: r[1].phone_number
        });
        if (r[1].is_sponsor) {
          const known_coord = r[0].find(x => x.id === r[1].id);
          if (known_coord) {
            this.fieldTeamCoordErForm.patchValue(
              {
                users: [known_coord.id]
              });
          }
        } else if (r[1].is_delegate) {
          const known_coords = r[0].filter(x => r[1].delegate_for.includes(x.id));
          if (known_coords) {
            this.fieldTeamCoordErForm.patchValue(
              {
                users: known_coords.map(x => x.id)
              });
          }
        }
      })
    ).subscribe();
    this.initAuthGroups();
    this.initReasons();
    this.initRoles();
  }

  submit() {
    this.submitting.next(true);
    this.responseService.post(this.fieldTeamCoordErForm.value).pipe(
      tap(() => {
        this.fieldTeamCoordErForm.reset();
        this.tags = [];
        this.saved.emit();
        this.matSnackBar.open('Request has been successfully submitted', 'Dismiss', {
          panelClass: ['snackbar-success'],
          verticalPosition: 'top'
        });
      }),
      finalize(() => this.submitting.next(false)),
      catchError(e => {
        const message = e.error.details ? e.error.details.join(', ') : 'Error';
        return of(this.matSnackBar.open(message, 'Dismiss', {
          verticalPosition: 'top',
          panelClass: ['snackbar-error']
        }));
      })
    ).subscribe();
  }

  initAuthGroups() {
    this.auth_groups = this.http.get<AgolGroup[]>('/v1/agol/groups/all/',
      {params: {is_auth_group: true}}
    );
  }

  initReasons() {
    this.reasons = this.responseService.options().pipe(
      map(r => r.actions.POST.default_reason.choices)
    );
  }

  initRoles() {
    this.roles = this.roleService.getList<AGOLRole>({is_available: true}).pipe(
      map(r => r.results),
      tap(r => {
        const default_role = r.find(x => x.system_default);
        if (default_role) {
          this.fieldTeamCoordErForm.patchValue({role: default_role.id});
        }
      })
    );
  }

}
