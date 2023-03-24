import {Component, OnInit} from '@angular/core';
import {LoginService} from './auth/login.service';
import {BehaviorSubject, Observable, ReplaySubject, Subject} from 'rxjs';
import {NavigationEnd, Router, ActivatedRoute} from '@angular/router';
import {UserConfig, UserConfigService} from './auth/user-config.service';
import {environment} from '../environments/environment';
import {filter} from 'rxjs/operators';

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
    public userConfig: UserConfigService
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
    this.admin_url = `${environment.api_url}/admin/`;
    this.config = this.userConfig.config;
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
}
