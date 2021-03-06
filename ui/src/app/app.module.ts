import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {RequestFormComponent} from './request-form/request-form.component';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatNativeDateModule, MatRippleModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDialogModule } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSliderModule } from '@angular/material/slider';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {HTTP_INTERCEPTORS, HttpClientModule, HttpClientXsrfModule} from '@angular/common/http';
import {CdkTableModule} from '@angular/cdk/table';
import {RECAPTCHA_SETTINGS, RecaptchaModule, RecaptchaSettings, RecaptchaFormsModule} from 'ng-recaptcha';
import {ApprovalListComponent} from './approval-list/approval-list.component';
import {FieldCoordListComponent} from './field-coord-list/field-coord-list.component';
import {LoadingService} from './services/loading.service';
import {HttpRequestInterceptor} from './http-request.interceptor';
import { ConfirmApprovalDialogComponent } from './dialogs/confirm-approval-dialog/confirm-approval-dialog.component';
import { EditAccountPropsDialogComponent } from './dialogs/edit-account-props-dialog/edit-account-props-dialog.component';
import { RequestFieldCoordDialogComponent } from './dialogs/request-field-coord-dialog/request-field-coord-dialog.component';
import {environment} from '../environments/environment';
import {FilterInputComponent} from './filter-input/filter-input.component';
import { HomeComponent } from './home/home.component';
import { FieldCoordErRequestFormComponent } from './field-coord-er-request-form/field-coord-er-request-form.component';
import {AuthModule} from './auth/auth.module';


@NgModule({
  declarations: [
    AppComponent,
    RequestFormComponent,
    ApprovalListComponent,
    ConfirmApprovalDialogComponent,
    EditAccountPropsDialogComponent,
    RequestFieldCoordDialogComponent,
    FilterInputComponent,
    HomeComponent,
    FieldCoordListComponent,
    FieldCoordErRequestFormComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    CdkTableModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    // MatStepperModule,
    MatDatepickerModule,
    MatDialogModule,
    MatExpansionModule,
    MatGridListModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatMenuModule,
    MatNativeDateModule,
    MatPaginatorModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatRippleModule,
    MatSelectModule,
    MatSidenavModule,
    MatSliderModule,
    MatSlideToggleModule,
    MatSnackBarModule,
    MatSortModule,
    MatTableModule,
    MatTabsModule,
    MatToolbarModule,
    MatTooltipModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatSidenavModule,
    // RestangularModule.forRoot([LoginService], RestangularConfigFactory),
    FormsModule,
    ReactiveFormsModule,
    RecaptchaModule,
    RecaptchaFormsModule,
    AuthModule,
    HttpClientXsrfModule.withOptions({ cookieName: 'csrftoken', headerName: 'X-CSRFToken' }),
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
