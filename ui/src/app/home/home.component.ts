import { Component, OnInit } from '@angular/core';
import {Router} from '@angular/router';
import {LoginService} from '../services/login.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  constructor(public loginService: LoginService, private router: Router) { }

  ngOnInit() {
  }

  navigateToUri(uri) {
    this.router.navigateByUrl(uri);
  }

}
