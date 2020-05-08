import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {HomeComponent} from './home/home.component';
import {RequestFormComponent} from './request-form/request-form.component';
import {ApprovalListComponent} from './approval-list/approval-list.component';
import {FieldCoordListComponent} from './field-coord-list/field-coord-list.component';
import {FieldCoordErRequestFormComponent} from './field-coord-er-request-form/field-coord-er-request-form.component';
import {LoginService} from './auth/login.service';

const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: 'accounts', canActivateChild: [LoginService],
    children: [
      {path: 'list', component: ApprovalListComponent}
    ]
  },
  {path: 'field-coordinators', component: FieldCoordListComponent},
  {path: 'field-coordinator-er-request',
    component: FieldCoordErRequestFormComponent,
    canActivate: [LoginService]
  },
  {path: 'requestaccount', component: RequestFormComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
