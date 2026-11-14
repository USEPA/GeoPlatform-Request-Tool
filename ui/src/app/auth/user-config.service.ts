import {Injectable} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {Observable, ReplaySubject} from 'rxjs';
import {map, share, tap} from 'rxjs/operators';
import {environment} from "@environments/environment";

export interface UserConfig {
  id: number;
  portal: string;
  portal_id: number;
  portal_requires_auth_group: boolean;
  name: string;
  permissions: string[];
  is_superuser: boolean;
  is_staff: boolean;
  is_sponsor: boolean;
  is_delegate: boolean;
  delegate_for: number[];
  phone_number: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserConfigService {
  config: ReplaySubject<UserConfig | null> = new ReplaySubject<UserConfig | null>(1);
  private current_config: UserConfig | null = null;
  public authenticated = false;
  constructor(public http: HttpClient) {
    this.config.pipe(share()).subscribe(config => this.current_config = config);
    this.loadConfig().subscribe();
  }

  loadConfig(): Observable<UserConfig> {
    return this.http.get<UserConfig>(`${environment.local_service_endpoint}/current_user/`).pipe(
      tap(() => this.authenticated = true),
      tap(config => this.config.next(config))
    );
  }

  clearConfig() {
    this.authenticated = false;
    this.config.next(null);
  }

  // checkGroups(groups: string[]) {
  //   if (this.current_config.is_superuser) {
  //     return true;
  //   }
  //   for (const group of groups) {
  //     if (this.current_config.groups.includes(group)) {
  //       return true;
  //     }
  //   }
  //   return false;
  // }

  checkPermissions(permission: string): boolean {
    return this.current_config !== null &&
      (this.current_config.is_superuser || this.current_config.permissions.includes(permission));
  }
}
