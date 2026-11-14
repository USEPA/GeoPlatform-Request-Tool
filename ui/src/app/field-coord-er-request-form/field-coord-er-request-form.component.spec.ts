import {beforeEach, describe, expect, it} from "vitest";
import {ComponentFixture, TestBed} from '@angular/core/testing';

import {FieldCoordErRequestFormComponent} from './field-coord-er-request-form.component';
import {provideHttpClientTesting} from '@angular/common/http/testing';
import {LoadingService} from '@services/loading.service';
import {provideHttpClient, withInterceptorsFromDi, withXhr} from '@angular/common/http';
import {UserConfigService} from '../auth/user-config.service';

describe('FieldCoordErRequestFormComponent', () => {
  let component: FieldCoordErRequestFormComponent;
  let fixture: ComponentFixture<FieldCoordErRequestFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FieldCoordErRequestFormComponent],
      providers: [
        {provide: LoadingService, useValue: {}},
        provideHttpClient(withXhr(), withInterceptorsFromDi()),
        provideHttpClientTesting()
      ]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FieldCoordErRequestFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should clear the requester and portal when the user logs out', () => {
    component.fieldTeamCoordErForm.patchValue({requester: 1, portal: 1});

    TestBed.inject(UserConfigService).clearConfig();
    fixture.detectChanges();

    expect(component.fieldTeamCoordErForm.controls.requester.value).toBeNull();
    expect(component.fieldTeamCoordErForm.controls.portal.value).toBeNull();
  });
});
