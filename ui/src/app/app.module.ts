import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {NoopAnimationsModule} from '@angular/platform-browser/animations';
import {HTTP_INTERCEPTORS, HttpClientModule, HttpClientXsrfModule} from '@angular/common/http';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {CdkTableModule} from '@angular/cdk/table';
import {RECAPTCHA_SETTINGS, RecaptchaModule, RecaptchaSettings, RecaptchaFormsModule} from 'ng-recaptcha';
import {CustomMaterialModule} from './core/material.module';
import { ToastrModule } from 'ngx-toastr';

import {environment} from '@environments/environment';
import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {AuthModule} from './auth/auth.module';
import { HomeComponent } from './home/home.component';
import {RequestFormComponent} from './request-form/request-form.component';
import {ApprovalListComponent} from './approval-list/approval-list.component';
import {FieldCoordListComponent} from './field-coord-list/field-coord-list.component';
import {HttpRequestInterceptor} from './http-request.interceptor';
import { ConfirmApprovalDialogComponent } from './dialogs/confirm-approval-dialog/confirm-approval-dialog.component';
import { EditAccountPropsDialogComponent } from './dialogs/edit-account-props-dialog/edit-account-props-dialog.component';
import { RequestFieldCoordDialogComponent } from './dialogs/request-field-coord-dialog/request-field-coord-dialog.component';
import {FilterInputComponent} from './filter-input/filter-input.component';
import { FieldCoordErRequestFormComponent } from './field-coord-er-request-form/field-coord-er-request-form.component';
import { ChooseCreationMethodComponent } from './dialogs/choose-creation-method/choose-creation-method.component';
import { GenericConfirmDialogComponent } from './dialogs/generic-confirm-dialog/generic-confirm-dialog.component';
import {TagInputComponent} from '@components/tag-input/tag-input.component';
import {LoadingService} from '@services/loading.service';
import { ResponseProjectRequestDialogComponent } from './dialogs/response-project-request-dialog/response-project-request-dialog.component';
import {CommonModule} from '@angular/common';



@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    RequestFormComponent,
    ApprovalListComponent,
    ConfirmApprovalDialogComponent,
    EditAccountPropsDialogComponent,
    RequestFieldCoordDialogComponent,
    FilterInputComponent,
    TagInputComponent,
    FieldCoordListComponent,
    FieldCoordErRequestFormComponent,
    ChooseCreationMethodComponent,
    GenericConfirmDialogComponent,
    ResponseProjectRequestDialogComponent
  ],
  imports: [
    CommonModule,
    BrowserModule,
    AuthModule,
    AppRoutingModule,
    CdkTableModule,
    HttpClientModule,
    BrowserAnimationsModule,
    // RestangularModule.forRoot([LoginService], RestangularConfigFactory),
    FormsModule,
    ReactiveFormsModule,
    RecaptchaModule,
    CustomMaterialModule,
    RecaptchaFormsModule,
    HttpClientXsrfModule.withOptions({ cookieName: 'requestcsrftoken', headerName: 'X-CSRFToken' }),
    ToastrModule.forRoot({
      timeOut: environment.snackbar_duration,
      positionClass: 'toast-bottom-center',
      preventDuplicates: true,
    }),
  ],
  providers: [{
    provide: RECAPTCHA_SETTINGS,
    useValue: {
      siteKey: environment.recaptcha_siteKey
    } as RecaptchaSettings,
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: HttpRequestInterceptor,
      multi: true
    },
    LoadingService,
  ],
  bootstrap: [AppComponent],
  entryComponents: [
    ConfirmApprovalDialogComponent,
    EditAccountPropsDialogComponent,
    RequestFieldCoordDialogComponent
  ]
})
export class AppModule {
}
