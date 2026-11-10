import { beforeEach, describe, expect, it } from "vitest";
import { TestBed, inject } from '@angular/core/testing';

import { BaseService } from './base.service';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { B } from '@angular/cdk/keycodes';
import { HttpClient, provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import { LoadingService } from '@services/loading.service';

let service: BaseService;

describe('BaseService', () => {

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [],
            providers: [provideHttpClient(withXhr(), withInterceptorsFromDi()), provideHttpClientTesting()]
        });
        service = new BaseService('', {} as HttpClient, {} as LoadingService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
