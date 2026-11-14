import { beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditAccountPropsDialogComponent, Sponsor } from './edit-account-props-dialog.component';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import { UserConfigService } from '../../auth/user-config.service';

describe('EditAccountPropsDialogComponent', () => {
    let component: EditAccountPropsDialogComponent;
    let fixture: ComponentFixture<EditAccountPropsDialogComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [EditAccountPropsDialogComponent],
            providers: [
                { provide: MatDialogRef, useValue: {} },
                { provide: MAT_DIALOG_DATA, useValue: {} },
                provideHttpClient(withXhr(), withInterceptorsFromDi()),
                provideHttpClientTesting()
            ]
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(EditAccountPropsDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should clear sponsors when the user logs out', () => {
        component.editAccountPropsForm.controls.sponsor.setValue(1);
        const sponsors: Sponsor[][] = [];
        component.sponsors.subscribe(value => sponsors.push(value));

        TestBed.inject(UserConfigService).clearConfig();
        fixture.detectChanges();

        expect(sponsors).toEqual([[]]);
        expect(component.editAccountPropsForm.controls.sponsor.value).toBeNull();
    });

    it('should cancel pending sponsor requests when the user logs out', () => {
        const httpTestingController = TestBed.inject(HttpTestingController);
        httpTestingController.expectOne(request => request.url.endsWith('/current_user/'))
            .flush({id: 1, is_sponsor: true});
        const request = httpTestingController.expectOne(request => request.url.endsWith('/v1/sponsors/1/'));

        TestBed.inject(UserConfigService).clearConfig();

        expect(request.cancelled).toBe(true);
    });
});
