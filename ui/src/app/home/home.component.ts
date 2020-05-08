import { Component, OnInit } from '@angular/core';
import {Router} from '@angular/router';
import {LoginService} from '../auth/login.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  teamCoordinatorsToolTip = 'View contact information for existing Team Coordinators or request to become a Team Coordinator';
  erRequestToolTip = 'Request to configure a new Response or Project';
  geoPlatformRequestToolTip = 'Request GeoPlatform user accounts';

  constructor(public loginService: LoginService, private router: Router) { }

  ngOnInit() {
  }

  navigateToUri(uri) {
    this.router.navigateByUrl(uri);
  }

}
