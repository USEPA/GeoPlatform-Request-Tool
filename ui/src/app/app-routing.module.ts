import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {RequestFormComponent} from './request-form/request-form.component';
import {LoginComponent} from './login/login.component';
import {OauthcallbackComponent} from './oauthcallback/oauthcallback.component';
import {LoginService} from './services/login.service';
import {ApprovalListComponent} from './approval-list/approval-list.component';

const routes: Routes = [
  {path: 'login', component: LoginComponent},
  {path: 'oauthcallback', component: OauthcallbackComponent},
  {path: '', component: RequestFormComponent},
  {path: 'accounts', canActivateChild: [LoginService],
    children: [
      {path: 'list', component: ApprovalListComponent}
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
