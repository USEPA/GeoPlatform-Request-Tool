import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {HomeComponent} from './home/home.component';
import {RequestFormComponent} from './request-form/request-form.component';
import {LoginComponent} from './login/login.component';
import {OauthcallbackComponent} from './oauthcallback/oauthcallback.component';
import {LoginService} from './services/login.service';
import {ApprovalListComponent} from './approval-list/approval-list.component';
import {FieldCoordListComponent} from './field-coord-list/field-coord-list.component';

const routes: Routes = [
  {path: 'login', component: LoginComponent},
  {path: 'oauthcallback', component: OauthcallbackComponent},
  {path: '', component: HomeComponent},
  {path: 'accounts', canActivateChild: [LoginService],
    children: [
      {path: 'list', component: ApprovalListComponent}
    ]
  },
  {path: 'field-coordinators', component: FieldCoordListComponent},
  {path: 'requestaccount', component: RequestFormComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
