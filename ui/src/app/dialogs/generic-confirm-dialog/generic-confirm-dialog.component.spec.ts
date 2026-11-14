import { beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenericConfirmDialogComponent } from './generic-confirm-dialog.component';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';

describe('GenericConfirmDialogComponent', () => {
    let component: GenericConfirmDialogComponent;
    let fixture: ComponentFixture<GenericConfirmDialogComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [GenericConfirmDialogComponent],
            imports: [
                MatDialogModule
            ],
            providers: [
                { provide: MatDialogRef, useValue: {} },
                { provide: MAT_DIALOG_DATA, useValue: {} }
            ]
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(GenericConfirmDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
