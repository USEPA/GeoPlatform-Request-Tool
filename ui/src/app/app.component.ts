import {Component, OnInit} from '@angular/core';
import {LoginService} from './auth/login.service';
import {BehaviorSubject, Observable, ReplaySubject, Subject} from 'rxjs';
import {NavigationEnd, Router, ActivatedRoute} from '@angular/router';
import {UserConfig, UserConfigService} from './auth/user-config.service';
import {environment} from '../environments/environment';
import {filter, tap} from 'rxjs/operators';
import {MatLegacySnackBar as MatSnackBar} from '@angular/material/legacy-snack-bar';

declare var gtag;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  admin_url: string;
  config: Observable<UserConfig>;

  constructor(
    public loginService: LoginService,
    public router: Router,
    public route: ActivatedRoute,
    public userConfig: UserConfigService,
    public snackBar: MatSnackBar
  ) {
    const navEndEvent$ = router.events.pipe(
      filter(e => e instanceof NavigationEnd)
    );
    navEndEvent$.subscribe((e: NavigationEnd) => {
      window['dataLayer'].push({
        event: 'navigation',
        pageName: e.url
      });
    });
  }

  ngOnInit(): void {
    this.admin_url = `${environment.local_service_endpoint}/admin/`;
    this.config = this.userConfig.config;
    this.route.queryParams.pipe(
      filter(q => 'redirect' in q),
      tap(() => this.open_redirect_message())
    ).subscribe()
  }

  logout() {
    this.loginService.logout().subscribe(() => this.router.navigate(['']));
  }

  switch_portal() {
    this.loginService.logout().subscribe(()=>this.router.navigate(['login'], {queryParams: {next: this.router.url}}))
  }
  close_warning() {
    this.router.navigate([]);
  }

  open_redirect_message() {
    // this.router.navigate([], {queryParams: {redirect: null}, queryParamsHandling: 'merge'})
    this.snackBar.open(
      'The Account Request Tool has a new home. Please update your bookmarks to https://gpdashboard.epa.gov/request/',
      'Dismiss',
      {verticalPosition: 'top', panelClass: ['snackbar-error']})
  }
}
