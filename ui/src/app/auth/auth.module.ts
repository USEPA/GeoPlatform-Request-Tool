import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {LoginComponent} from './login/login.component';
import {LoginService} from './login.service';
import {MatCardModule} from '@angular/material/card';
import {HttpClientModule} from '@angular/common/http';
import {RouterModule} from '@angular/router';
import {MatButtonModule} from '@angular/material/button';
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
