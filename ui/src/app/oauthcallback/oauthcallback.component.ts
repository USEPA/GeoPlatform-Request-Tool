import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, ParamMap, Router} from '@angular/router';
import {switchMap, map, tap} from 'rxjs/operators';
import {environment} from '../../environments/environment';
import {LoginService} from '../services/login.service';

@Component({
  selector: 'app-oauthcallback',
  templateUrl: './oauthcallback.component.html',
  styleUrls: ['./oauthcallback.component.css']
})
export class OauthcallbackComponent implements OnInit {

  constructor(public route: ActivatedRoute, public loginService: LoginService, public router: Router) {
  }

  ngOnInit() {
    this.route.fragment.pipe(
      switchMap(fragment => {
        let oauth_params = fragment.match('(access_token=)(.*)(&expires_in=)(.*)(&username=)(.*)(&ssl=)');

        return this.loginService.convertToken(oauth_params[2], oauth_params[4], oauth_params[6]);
      }),
      tap(() => this.router.navigate(['/accounts/list/']))
    ).subscribe();
  }

}
