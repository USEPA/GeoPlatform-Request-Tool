import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { of } from 'rxjs';

import { ResponseProjectRequestDialogComponent } from './response-project-request-dialog.component';
import { MatDialogRef } from '@angular/material/dialog';
import {LoadingService} from "@services/loading.service";
import { UserConfigService } from '../../auth/user-config.service';

describe('ResponseProjectRequestDialogComponent', () => {
    let component: ResponseProjectRequestDialogComponent;
    let fixture: ComponentFixture<ResponseProjectRequestDialogComponent>;
    let httpTestingController: HttpTestingController;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ResponseProjectRequestDialogComponent],
            providers: [
              {provide: LoadingService, useValue: {}},
                { provide: MatDialogRef, useValue: {} },
                {
                    provide: UserConfigService,
                    useValue: { config: of({ id: 1, portal_requires_auth_group: false }) }
                },
                provideHttpClient(),
                provideHttpClientTesting()
            ]
        })
            .compileComponents();
        httpTestingController = TestBed.inject(HttpTestingController);
    });

    afterEach(() => httpTestingController.verify());

    beforeEach(() => {
        fixture = TestBed.createComponent(ResponseProjectRequestDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();

        httpTestingController.expectOne(request => request.url.endsWith('/v1/responses/'))
            .flush({ actions: { POST: { default_reason: { choices: [] } } } });
        httpTestingController.expectOne(request => request.url.endsWith('/v1/agol/roles/'))
            .flush({ count: 0, results: [] });
    });
});
