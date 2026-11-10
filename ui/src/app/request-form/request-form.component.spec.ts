import { beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestFormComponent } from './request-form.component';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { MatSnackBar, MatSnackBarRef } from '@angular/material/snack-bar';
import { RouterTestingModule } from '@angular/router/testing';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import {MatCard, MatCardSubtitle, MatCardTitle} from "@angular/material/card";
import {MatFormField, MatHint, MatLabel} from "@angular/material/input";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {provideRouter} from "@angular/router";

describe('RequestFormComponent', () => {
    let component: RequestFormComponent;
    let fixture: ComponentFixture<RequestFormComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [RequestFormComponent],
            providers: [
                { provide: MatSnackBar, useValue: {} },
                provideHttpClient(withXhr(), withInterceptorsFromDi()),
                provideHttpClientTesting(),
              provideRouter([])
            ]
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(RequestFormComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
