import {Component, OnInit, ChangeDetectionStrategy} from '@angular/core';
import { HttpXsrfTokenExtractor } from '@angular/common/http';
import {LoginService} from '../login.service';
import {ActivatedRoute, ParamMap, Router} from '@angular/router';
import {map, catchError, tap} from 'rxjs/operators';
import {Observable} from "rxjs";


@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css'],
    changeDetection: ChangeDetectionStrategy.Eager,
    standalone: false
})
export class LoginComponent implements OnInit {
  username!: string;
  password!: string;
  showNewUserMessage = false;
  geosecure!: boolean;
  geoportal!: boolean;
  ready = false;
  constructor(public loginService: LoginService, public route: ActivatedRoute, public router: Router,
              private xsrfTokenExtractor: HttpXsrfTokenExtractor) {
  }

  ngOnInit() {
    this.checkQueryParams();
    this.startLogin().subscribe(() => {
      this.ready = true;
    });
  }

  startLogin(): Observable<any> {
    return this.loginService.startLogin();
  }

  getLoginUrl(loginType: string): string {
    return this.loginService.getLoginUrl(loginType);
  }

  get nextUrl(): string {
    return window.location.origin + (this.route.snapshot.queryParams.next || '');
  }

  get csrfToken(): string {
    return this.xsrfTokenExtractor.getToken() || '';
  }

  checkQueryParams() {
    const next = this.route.snapshot.queryParams.next || '';
    this.showNewUserMessage = next.includes('new_response=true');
    this.geosecure = next.toLowerCase().includes('#geosecure');
    this.geoportal = next.toLowerCase().includes('#geoplatform');
  }

  // can not use b/c it would break mapping
  // loginWithCredentials() {
  //   this.login_error = '';
  //   this.loginService.login(this.username, this.password).pipe(
  //     catchError(error => {
  //       let error_object = JSON.parse(error.error);
  //       this.login_error = error_object.non_field_errors[0];
  //     }),
  //     map(response => this.router.navigate(['dashboard']))
  //   ).subscribe();
  // }
}
