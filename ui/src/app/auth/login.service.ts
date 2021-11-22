import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {catchError, map, switchMap} from 'rxjs/operators';
import {BehaviorSubject, Observable} from 'rxjs';
import {Router, ActivatedRouteSnapshot, CanActivateChild, RouterStateSnapshot, CanActivate} from '@angular/router';
import {environment} from '../../environments/environment';
import {UserConfigService} from './user-config.service';
import {Location} from '@angular/common';
// import {error} from 'util';

// interface TokenResponse {
//   access_token: string;
//   expires_in: number;
//   token_type: string;
//   scope: string;
//   refresh_token: string;
// }

@Injectable()
export class LoginService implements CanActivateChild, CanActivate {
  // login service type event
  public loginTypeSource: BehaviorSubject<string> = new BehaviorSubject<string>('');
  public loginTypeEvent: Observable<string> = this.loginTypeSource.asObservable();
  // access_token;
  // token_expires: Date;
  // username: string;
  // display_name: string;
  // client_id: string;
  // response_type: string;
  // redirect_uri: string;
  // local_client_id: string;
  // oauth_url: string;
  // esri_token_object: any;
  // access_token_type: string;
  // groups: string[];
  // permissions: string[];
  // is_superuser: boolean;

  constructor(private http: HttpClient, private router: Router, private configService: UserConfigService,
              private location: Location) {
    // this.loginTypeEvent.subscribe((loginType) => {
    //   if (loginType) {
    //     localStorage.setItem('loginType', loginType);
    //   }
    //   if (localStorage.getItem('loginType') === 'agol') {
    //     this.client_id = environment.agol.oauth_client_id;
    //     this.response_type = environment.agol.oauth_response_type;
    //     this.redirect_uri = environment.agol.oauth_redirect_uri;
    //     this.local_client_id = environment.agol.local_client_id;
    //     this.oauth_url = environment.agol.oauth_url;
    //   } else if (localStorage.getItem('loginType') === 'sharepoint') {
    //     this.client_id = environment.share_point.oauth_client_id;
    //     this.response_type = environment.share_point.oauth_response_type;
    //     this.redirect_uri = environment.share_point.oauth_redirect_uri;
    //     this.local_client_id = environment.share_point.local_client_id;
    //     this.oauth_url = environment.share_point.oauth_url;
    //   }
    // });
  }

  canActivateChild(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
    return new Promise(resolve => {

      this.configService.loadConfig().pipe(
        switchMap(() => {
            return this.configService.config.pipe(
              map(() => {
                resolve(true);
              }));
          }
        ),
        catchError(() => this.router.navigate(['login'], {queryParams: {next: this.location.prepareExternalUrl(state.url)}}))
      ).subscribe();

    });
  }

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
    return new Promise(resolve => {

      this.configService.loadConfig().pipe(
        switchMap(() => {
            return this.configService.config.pipe(
              map(() => {
                resolve(true);
              }));
          }
        ),
        catchError(() => this.router.navigate(['login']))
      ).subscribe();

    });
  }

  sendToLogin(provider: string, next: string = '') {
    window.location.href = `${environment.oauth_url}/login/${provider}/?next=${next}`;
  }

  // convertToken(accessToken: string) {
  //   // return forkJoin(
  //   //   this.setEsriToken(access_token, expires_in, user_id),
  //   return this.http.post<TokenResponse>(`http://localhost:8000/complete/agol/`, '', {
  //     params: new HttpParams()
  //       // .set('grant_type', 'convert_token')
  //       // .set('client_id', this.local_client_id)
  //       // .set('backend', 'agol')
  //       .set('code', accessToken)
  //   }).pipe(
  //     // switchMap(response => {
  //     //   this.setAccessToken(response.access_token, response.expires_in, response.token_type);
  //     //   return this.configService.loadConfig();
  //     // })
  //   );
  // }
  //
  // login(username: string, password: string) {
  //   const data = {
  //     username: username,
  //     password: password
  //   };
  //   return this.http.post(`/rest-auth/login/`, data)
  //     .pipe(
  //       map(response => this.setAccessToken(response['key'], 3600, 'Token'))
  //     );
  // }


  // setEsriToken(access_token: string, expires_in: string, user_id: string) {
  //   return new Observable(obs => {
  //     loadModules(['esri/identity/IdentityManager', 'esri/identity/OAuthInfo'])
  //       .then(([IdentityManager, OAuthInfo]) => {
  //         const info = new OAuthInfo({
  //           appId: environment.oauth_client_id,
  //           portalUrl: 'https://epa.maps.arcgis.com'
  //         });
  //         IdentityManager.registerOAuthInfos([info]);
  //         this.esri_token_object = {
  //           expires: expires_in,
  //           server: `https://epa.maps.arcgis.com/sharing`,
  //           ssl: true,
  //           token: access_token,
  //           userId: user_id
  //         };
  //         IdentityManager.registerToken(this.esri_token_object);
  //         localStorage.setItem('esri_oauth_token', JSON.stringify(this.esri_token_object));
  //         obs.next();
  //         obs.complete();
  //       });
  //   });
  // }

  // setAccessToken(accessToken: string, expiresIn: number, tokenType: string) {
  //   localStorage.setItem('access_token', accessToken);
  //   this.access_token = accessToken;
  //   localStorage.setItem('access_token_type', tokenType);
  //   this.access_token_type = tokenType;
  //   const now = new Date().getTime();
  //   this.token_expires = new Date(now + (expiresIn * 1000));
  //   localStorage.setItem('token_expires', this.token_expires.toISOString());
  // }
  //
  // loadToken() {
  //   return iif(() => this.isTokenValid(),
  //     of(true),
  //     new Observable(obs => {
  //       const expirationDate = String(localStorage.getItem('token_expires'));
  //       this.token_expires = expirationDate !== 'null' ? new Date(expirationDate) : new Date();
  //       this.access_token = localStorage.getItem('access_token');
  //       this.access_token_type = localStorage.getItem('access_token_type');
  //       if (this.access_token) {
  //         this.configService.loadConfig().subscribe();
  //         obs.next();
  //         obs.complete();
  //       } else {
  //         obs.error();
  //       }
  //     })
  //   );
  // }

  // loadEsriToken() {
  //   this.esri_token_object = JSON.parse(localStorage.getItem('esri_oauth_token'));
  //   return loadModules(['esri/identity/IdentityManager', 'esri/identity/OAuthInfo'])
  //     .then(([IdentityManager, OAuthInfo]) => {
  //       const info = new OAuthInfo({
  //         appId: environment.oauth_client_id,
  //         portalUrl: 'https://epa.maps.arcgis.com'
  //       });
  //       IdentityManager.registerOAuthInfos([info]);
  //       IdentityManager.registerToken(this.esri_token_object);
  //     });
  // }

  // isTokenValid() {
  //   const now = new Date();
  //   return (this.token_expires > now);
  // }
  //
  // clearToken() {
  //   delete this.token_expires;
  //   delete this.access_token;
  //   localStorage.clear();
  // }

  logout() {
    this.configService.clearConfig();
    // this.clearToken();
    return this.http.post(`/auth/logout/`, '', {responseType: 'text'});
  }


}
