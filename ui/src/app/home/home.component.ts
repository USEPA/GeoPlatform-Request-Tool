import {Component, OnInit, ChangeDetectionStrategy} from '@angular/core';
import {ActivatedRoute, Router, RouterLink} from '@angular/router';
import {LoginService} from '../auth/login.service';
import {MatDialog} from '@angular/material/dialog';
import {ResponseProjectRequestDialogComponent} from '../dialogs/response-project-request-dialog/response-project-request-dialog.component';
import {Observable, take} from 'rxjs';
import {filter, map, tap} from 'rxjs/operators';
import {UserConfigService} from '../auth/user-config.service';
import {AsyncPipe} from "@angular/common";
import {RequestFormComponent} from "../request-form/request-form.component";
import {MatButton} from "@angular/material/button";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  changeDetection: ChangeDetectionStrategy.Eager,
  imports: [
    AsyncPipe,
    RequestFormComponent,
    MatButton,
    RouterLink
  ]
})
export class HomeComponent implements OnInit {
  isResponseInURL!: Observable<boolean>;

  constructor(public loginService: LoginService, private router: Router, private dialog: MatDialog,
              private route: ActivatedRoute, private userConfig: UserConfigService) {
  }

  ngOnInit() {
    this.isResponseInURL = this.route.queryParamMap.pipe(
      map(params => params.has('response'))
    );
    if (this.route.snapshot.queryParams.new_response === 'true') {
      this.userConfig.config.pipe(
        filter(c => !!c),
        tap(() => {
          this.openResponseRequestDialog();
          this.clearResponseQueryParam();
        }),
        take(1)
      ).subscribe();
    }
  }

  navigateToUri(uri: string) {
    this.router.navigateByUrl(uri);
  }

  openResponseRequestDialog() {
    if (this.userConfig.authenticated) {
      this.dialog.open(ResponseProjectRequestDialogComponent,
        {width: '700px'}
      ).afterClosed().pipe(
        tap(() => this.clearResponseQueryParam())
      ).subscribe();
    } else {
      this.router.navigate(['login'], {queryParams: {next: `${window.location.pathname}?new_response=true`}});
    }
  }

  clearResponseQueryParam() {
    this.router.navigate([''], {queryParams: {new_response: null}, queryParamsHandling: 'merge'});
  }

}
