import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {LoginComponent} from './login/login.component';
import {LoginService} from './login.service';
import {MatLegacyCardModule as MatCardModule} from '@angular/material/legacy-card';
import {HttpClientModule} from '@angular/common/http';
import {RouterModule} from '@angular/router';
import {MatLegacyButtonModule as MatButtonModule} from '@angular/material/legacy-button';
import {AuthRoutingModule} from './auth-routing.module';



@NgModule({
  declarations: [LoginComponent],
  exports: [LoginComponent],
  imports: [
    CommonModule,
    MatCardModule,
    HttpClientModule,
    RouterModule,
    MatButtonModule,
    AuthRoutingModule
  ],
  providers: [LoginService]
})
export class AuthModule { }
