import { Component, OnInit } from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {LoginService} from '../auth/login.service';
import {MatDialog} from '@angular/material/dialog';
import {ResponseProjectRequestDialogComponent} from '../dialogs/response-project-request-dialog/response-project-request-dialog.component';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  isResponseInURL: Observable<boolean>;
  constructor(public loginService: LoginService, private router: Router, private dialog: MatDialog,
              private route: ActivatedRoute) { }

  ngOnInit() {
    this.isResponseInURL = this.route.queryParamMap.pipe(
      map(params => params.has('response'))
    );
  }

  navigateToUri(uri) {
    this.router.navigateByUrl(uri);
  }

  openResponseRequestDialog() {
    this.dialog.open(ResponseProjectRequestDialogComponent,
      {width: '700px'}
    );
  }


}
