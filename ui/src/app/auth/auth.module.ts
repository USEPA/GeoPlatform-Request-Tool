import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {LoginComponent} from './login/login.component';
import {LoginService} from './login.service';
import {MatCardModule} from '@angular/material/card';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import {RouterModule} from '@angular/router';
import {MatButtonModule} from '@angular/material/button';
import {AuthRoutingModule} from './auth-routing.module';
import {MatProgressSpinner} from "@angular/material/progress-spinner";



@NgModule({ declarations: [LoginComponent],
    exports: [LoginComponent],
    imports: [CommonModule,
        MatCardModule,
        RouterModule,
        MatButtonModule,
        AuthRoutingModule, MatProgressSpinner], providers: [LoginService, provideHttpClient(withXhr(), withInterceptorsFromDi())] })
export class AuthModule { }
