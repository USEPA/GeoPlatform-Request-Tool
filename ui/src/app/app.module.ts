import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import { provideHttpClient, withInterceptorsFromDi, withXsrfConfiguration, withXhr } from '@angular/common/http';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {CdkTableModule} from '@angular/cdk/table';
import {CustomMaterialModule} from './core/material.module';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {AuthModule} from './auth/auth.module';
import {ApprovalListComponent} from './approval-list/approval-list.component';
import {FieldCoordListComponent} from './field-coord-list/field-coord-list.component';
import {ConfirmApprovalDialogComponent} from './dialogs/confirm-approval-dialog/confirm-approval-dialog.component';
import {FilterInputComponent} from './filter-input/filter-input.component';
import {ChooseCreationMethodComponent} from './dialogs/choose-creation-method/choose-creation-method.component';
import {GenericConfirmDialogComponent} from './dialogs/generic-confirm-dialog/generic-confirm-dialog.component';
import {LoadingService} from '@services/loading.service';
import {CommonModule} from '@angular/common';


@NgModule({
    declarations: [
        AppComponent,
        ApprovalListComponent,
        ConfirmApprovalDialogComponent,
        FilterInputComponent,
        FieldCoordListComponent,
        ChooseCreationMethodComponent,
        GenericConfirmDialogComponent,
    ],
    bootstrap: [AppComponent], imports: [CommonModule,
        BrowserModule,
        AuthModule,
        AppRoutingModule,
        CdkTableModule,
        FormsModule,
        ReactiveFormsModule,
        CustomMaterialModule],
  exports: [
    FilterInputComponent
  ],
    providers: [
        LoadingService,
        provideHttpClient(withXhr(), withInterceptorsFromDi(), withXsrfConfiguration({
            cookieName: 'requestcsrftoken',
            headerName: 'X-CSRFToken'
        })),
    ]
})
export class AppModule {
}
