import { beforeEach, describe, expect, it } from "vitest";
import { TestBed } from '@angular/core/testing';

import { UserConfigService } from './user-config.service';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';

describe('UserConfigService', () => {
    beforeEach(() => TestBed.configureTestingModule({
        imports: [],
        providers: [provideHttpClient(withXhr(), withInterceptorsFromDi()), provideHttpClientTesting()]
    }));

    it('should be created', () => {
        const service: UserConfigService = TestBed.inject(UserConfigService);
        expect(service).toBeTruthy();
    });
});
