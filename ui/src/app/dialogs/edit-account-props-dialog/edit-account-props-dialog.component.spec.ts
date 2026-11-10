import { beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditAccountPropsDialogComponent } from './edit-account-props-dialog.component';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';

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
});
