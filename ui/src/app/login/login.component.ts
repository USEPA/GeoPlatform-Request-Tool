import {Component, OnInit} from '@angular/core';
import {LoginService} from '../services/login.service';
import {ActivatedRoute, ParamMap, Router} from '@angular/router';
import {map, catchError, tap} from 'rxjs/operators';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  username: string;
  password: string;
  login_error: string;

  constructor(private loginService: LoginService, private route: ActivatedRoute, private router: Router) {
  }

  ngOnInit() {
  }

  login() {
    // let next: string;
    // if (!isUndefined(this.state.params.next)) next = this.state.params.next;
    // else next = 'root';
    this.loginService.sendToLogin();
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
