import { beforeEach, describe, expect, it } from "vitest";
import { TestBed, inject } from '@angular/core/testing';

import { LoginService } from './login.service';
import { AuthModule } from './auth.module';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import { UserConfig, UserConfigService } from './user-config.service';
import { environment } from '../../environments/environment';

describe('LoginService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [AuthModule,
                RouterTestingModule],
            providers: [provideHttpClient(withXhr(), withInterceptorsFromDi()), provideHttpClientTesting()]
        });
    });

    it('should be created', inject([LoginService], (service: LoginService) => {
        expect(service).toBeTruthy();
    }));

    it('should clear the user config safely when logging out', () => {
        const service = TestBed.inject(LoginService);
        const userConfig = TestBed.inject(UserConfigService);
        const httpTestingController = TestBed.inject(HttpTestingController);
        httpTestingController.expectOne(`${environment.local_service_endpoint}/current_user/`)
            .flush({id: 1, is_superuser: false, permissions: ['accounts.approve_account']});
        const configs: (UserConfig | null)[] = [];
        userConfig.config.subscribe(config => configs.push(config));

        service.logout().subscribe();

        expect(configs[configs.length - 1]).toBeNull();
        expect(userConfig.authenticated).toBe(false);
        expect(userConfig.checkPermissions('accounts.approve_account')).toBe(false);
        const request = httpTestingController.expectOne(`${environment.local_service_endpoint}/auth/logout/`);
        expect(request.request.method).toBe('POST');
        request.flush('');
        httpTestingController.verify();
    });
});
