import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {FieldCoordListComponent} from './field-coord-list.component';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {LoadingService} from '@services/loading.service';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatDialog} from '@angular/material/dialog';
import {LoginService} from '../auth/login.service';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatTableModule} from '@angular/material/table';
import {MatPaginatorModule} from '@angular/material/paginator';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {CdkTableModule} from '@angular/cdk/table';
import {MatInputModule} from '@angular/material/input';
import {NoopAnimationsModule} from '@angular/platform-browser/animations';

describe('FieldCoordListComponent', () => {
  let component: FieldCoordListComponent;
  let fixture: ComponentFixture<FieldCoordListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [FieldCoordListComponent],
      imports: [
        HttpClientTestingModule,
        MatSnackBarModule,
        MatSidenavModule,
        MatTableModule,
        MatPaginatorModule,
        FormsModule,
        ReactiveFormsModule,
        CdkTableModule,
        MatFormFieldModule,
        MatInputModule,
        NoopAnimationsModule
      ],
      providers: [
        {provide: LoadingService, useValue: {setLoading: () => {}}},
        {provide: LoginService, useValue: {}},
        {provide: MatDialog, useValue: {}}
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FieldCoordListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
