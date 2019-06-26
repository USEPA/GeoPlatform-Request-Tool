import {Component, OnInit} from '@angular/core';
import {LoginService} from './services/login.service';
import {BehaviorSubject, Observable, Subject} from 'rxjs';
import {Router} from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  constructor(public loginService: LoginService, public router: Router) {}
  ngOnInit(): void {

  }

  logout() {
    this.loginService.clearToken();
    this.router.navigate(['']);
  }
}
