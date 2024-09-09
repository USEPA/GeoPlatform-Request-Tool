import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestFormComponent } from './request-form.component';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {MatLegacySnackBar, MatLegacySnackBarRef} from '@angular/material/legacy-snack-bar';
import {RouterTestingModule} from '@angular/router/testing';
import {ReCaptchaV3Service} from 'ng-recaptcha';

describe('RequestFormComponent', () => {
  let component: RequestFormComponent;
  let fixture: ComponentFixture<RequestFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestFormComponent ],
      imports: [
        HttpClientTestingModule,
        RouterTestingModule
      ],
      providers: [
        {provide: MatLegacySnackBar, useValue: {}},
        {provide: ReCaptchaV3Service, useValue: {}},
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
