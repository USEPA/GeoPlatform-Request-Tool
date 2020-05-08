import {Injectable, Injector} from '@angular/core';
import {HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse} from "@angular/common/http";
import {Observable} from "rxjs";

// import {LoginService} from "./services/login.service";

import {tap} from 'rxjs/operators';
import {Router} from '@angular/router';
import {environment} from '../environments/environment';

@Injectable()
export class HttpRequestInterceptor implements HttpInterceptor {
  constructor(private injector: Injector, public router: Router) {
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (request.url.indexOf('http') === -1 && request.url.indexOf(environment.local_service_endpoint) === -1) {
      request = request.clone({
        withCredentials: true,
        url: environment.local_service_endpoint + request.url
      });
    }

    return next.handle(request).pipe(
      tap(event => {
        },
        err => {
          if (err instanceof HttpErrorResponse && err.status == 401) {
            // loginService.clearToken();
            this.router.navigate(['/login']);
          }
        }));
  }
}
