import {Component, OnInit} from '@angular/core';
import {LoginService} from './auth/login.service';
import {BehaviorSubject, Observable, Subject} from 'rxjs';
import {Router} from '@angular/router';
import {UserConfigService} from './auth/user-config.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  constructor(public loginService: LoginService, public router: Router, public userConfig: UserConfigService) {}
  ngOnInit(): void {

  }

  logout() {
    this.loginService.logout();
    this.router.navigate(['']);
  }
}
