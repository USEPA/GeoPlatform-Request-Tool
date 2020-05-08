import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable, ReplaySubject} from 'rxjs';
import {share, tap} from 'rxjs/operators';
import {environment} from '../../environments/environment';

export interface UserConfig {
  id: number;
  name: string;
  permissions: string[];
  is_superuser: boolean;
  groups: string[];
  ptt?: {
    id: number;
    name: string;
    group: number;
    group_name: string;
    request_url_slug: string;
    region: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class UserConfigService {
  config: ReplaySubject<UserConfig> = new ReplaySubject<UserConfig>();
  base_map_id: ReplaySubject<string> = new ReplaySubject<string>();
  private current_config: UserConfig;
  constructor(public http: HttpClient) {
    this.config.pipe(share()).subscribe(config => this.current_config = config);
    this.loadConfig();
  }

  loadConfig(): Observable<any> {
    return this.http.get(`/current_user/`).pipe(
      tap(config => this.config.next(config))
    );
  }

  clearConfig() {
    this.config.next();
  }

  checkGroups(groups: string[]) {
    if (this.current_config.is_superuser) {
      return true;
    }
    for (const group of groups) {
      if (this.current_config.groups.includes(group)) {
        return true;
      }
    }
    return false;
  }

  checkPermissions(permission: string) {
    return this.current_config.is_superuser ? this.current_config.is_superuser : this.current_config.permissions.includes(permission);
  }
}
