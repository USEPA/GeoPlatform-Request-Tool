import { beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestFieldCoordDialogComponent } from './request-field-coord-dialog.component';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { LoadingService } from '@services/loading.service';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';

describe('RequestFieldCoordDialogComponent', () => {
    let component: RequestFieldCoordDialogComponent;
    let fixture: ComponentFixture<RequestFieldCoordDialogComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [RequestFieldCoordDialogComponent],
            providers: [
                { provide: MatDialogRef, useValue: {} },
                { provide: LoadingService, useValue: {} },
                { provide: MAT_DIALOG_DATA, useValue: {} },
                provideHttpClient(withXhr(), withInterceptorsFromDi()),
                provideHttpClientTesting()
            ]
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(RequestFieldCoordDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
