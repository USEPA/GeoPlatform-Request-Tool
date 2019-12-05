import { Component, OnInit } from '@angular/core';
import {Router} from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  constructor(private router: Router) { }

  ngOnInit() {
  }

  navigateToFieldCoordinators() {
     this.router.navigateByUrl('/field-coordinators');
  }

  navigateToRequestAccount() {
     this.router.navigateByUrl('/requestaccount');
  }

}
