import { beforeEach, describe, expect, it } from "vitest";
import { TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { AppComponent } from './app.component';
import { LoadingService } from '@services/loading.service';
import { LoginService } from './auth/login.service';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';

describe('AppComponent', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            declarations: [
                AppComponent
            ],
            imports: [RouterTestingModule,
                MatToolbarModule,
                MatIconModule,
                MatSnackBarModule],
            providers: [
                { provide: LoadingService, useValue: {} },
                { provide: LoginService, useValue: {} },
                provideHttpClient(withXhr(), withInterceptorsFromDi()),
                provideHttpClientTesting()
            ]
        }).compileComponents();
    });

    it('should create the app', () => {
        const fixture = TestBed.createComponent(AppComponent);
        const app = fixture.debugElement.componentInstance;
        expect(app).toBeTruthy();
    });

});
