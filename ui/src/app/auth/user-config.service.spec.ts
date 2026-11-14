import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { TestBed } from '@angular/core/testing';

import { UserConfig, UserConfigService } from './user-config.service';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import { environment } from '../../environments/environment';

describe('UserConfigService', () => {
    let service: UserConfigService;
    let httpTestingController: HttpTestingController;
    const config: UserConfig = {
        id: 1,
        portal: 'geoplatform',
        portal_id: 1,
        portal_requires_auth_group: false,
        name: 'Test User',
        permissions: ['accounts.approve_account'],
        is_superuser: false,
        is_staff: false,
        is_sponsor: true,
        is_delegate: false,
        delegate_for: [],
        phone_number: ''
    };

    beforeEach(() => TestBed.configureTestingModule({
        imports: [],
        providers: [provideHttpClient(withXhr(), withInterceptorsFromDi()), provideHttpClientTesting()]
    }));

    beforeEach(() => {
        service = TestBed.inject(UserConfigService);
        httpTestingController = TestBed.inject(HttpTestingController);
    });

    afterEach(() => httpTestingController.verify());

    function loadConfig(userConfig = config) {
        httpTestingController.expectOne(`${environment.local_service_endpoint}/current_user/`).flush(userConfig);
    }

    it('should be created', () => {
        loadConfig();
        expect(service).toBeTruthy();
    });

    it('should deny permissions before the config loads', () => {
        expect(service.checkPermissions('accounts.approve_account')).toBe(false);
        loadConfig();
    });

    it('should preserve permission checks for authenticated users', () => {
        loadConfig();

        expect(service.authenticated).toBe(true);
        expect(service.checkPermissions('accounts.approve_account')).toBe(true);
        expect(service.checkPermissions('accounts.delete_account')).toBe(false);
    });

    it('should grant all permissions to superusers', () => {
        loadConfig({...config, is_superuser: true});

        expect(service.checkPermissions('accounts.delete_account')).toBe(true);
    });

    it('should emit null and revoke permissions synchronously on logout', () => {
        loadConfig({...config, is_superuser: true});
        const states: {config: UserConfig | null; authenticated: boolean; allowed: boolean}[] = [];
        service.config.subscribe(value => states.push({
            config: value,
            authenticated: service.authenticated,
            allowed: service.checkPermissions('accounts.approve_account')
        }));

        service.clearConfig();

        expect(states[states.length - 1]).toEqual({config: null, authenticated: false, allowed: false});
    });

    it('should replay only null to subscribers after logout', () => {
        loadConfig();
        service.clearConfig();
        const values: (UserConfig | null)[] = [];

        service.config.subscribe(value => values.push(value));

        expect(values).toEqual([null]);
    });

    it('should allow repeated logout and loading another user', () => {
        loadConfig();
        service.clearConfig();
        service.clearConfig();
        service.loadConfig().subscribe();
        loadConfig({...config, id: 2, permissions: []});

        expect(service.authenticated).toBe(true);
        expect(service.checkPermissions('accounts.approve_account')).toBe(false);
    });
});
