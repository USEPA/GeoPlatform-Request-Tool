import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoginComponent } from './login.component';
import { AuthModule } from '../auth.module';
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRoute } from '@angular/router';
import { HttpXsrfTokenExtractor, provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { environment } from '../../../environments/environment';

describe('LoginComponent', () => {
    let component: LoginComponent;
    let fixture: ComponentFixture<LoginComponent>;
    let httpTestingController: HttpTestingController;
    let csrfToken: string | null;

    beforeEach(async () => {
        csrfToken = null;
        await TestBed.configureTestingModule({
            imports: [AuthModule,
                RouterTestingModule],
            providers: [
                {
                    provide: HttpXsrfTokenExtractor,
                    useValue: { getToken: () => csrfToken }
                },
                {
                    provide: ActivatedRoute,
                    useValue: {
                        snapshot: {
                            queryParams: {
                                next: 'test'
                            }
                        }
                    }
                },
                provideHttpClient(withXhr(), withInterceptorsFromDi()),
                provideHttpClientTesting()
            ]
        })
            .compileComponents();
        httpTestingController = TestBed.inject(HttpTestingController);
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(LoginComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
        httpTestingController.expectOne(`${environment.local_service_endpoint}/current_user/`).flush({});
    });

    afterEach(() => {
        httpTestingController.verify();
    });

    function completeStartLogin() {
        const request = httpTestingController.expectOne(`${environment.local_service_endpoint}/start/`);
        expect(request.request.method).toBe('GET');
        request.flush({});
        csrfToken = 'test-csrf-token';
        fixture.detectChanges();
    }

    it('should create', () => {
        completeStartLogin();
        expect(component).toBeTruthy();
    });

    it('should wait for the CSRF token before rendering the login forms', () => {
        expect(component.ready).toBe(false);
        expect(component.csrfToken).toBe('');
        expect(fixture.nativeElement.querySelectorAll('form').length).toBe(0);

        completeStartLogin();

        const forms: HTMLFormElement[] = Array.from(fixture.nativeElement.querySelectorAll('form'));
        expect(forms.length).toBe(2);
        forms.forEach((form, index) => {
            const provider = index === 0 ? 'geoplatform' : 'geosecure';
            expect(form.method).toBe('post');
            expect(form.getAttribute('action')).toBe(`${environment.oauth_url}/login/${provider}/`);
            expect(new FormData(form).get('next')).toBe(window.location.origin + 'test');
            expect(form.querySelector('button')?.type).toBe('submit');
            expect((form.elements.namedItem('csrfmiddlewaretoken') as HTMLInputElement).value).toBe('test-csrf-token');
            const event = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(event);
            expect(event.defaultPrevented).toBe(false);
        });
    });

    it('should preserve the entire return URL including query parameters and fragments', () => {
        completeStartLogin();
        component.route.snapshot.queryParams.next = '/request/?new_response=true&project=1#geosecure';
        component.checkQueryParams();
        fixture.detectChanges();

        const forms: HTMLFormElement[] = Array.from(fixture.nativeElement.querySelectorAll('form'));
        expect(forms.length).toBe(1);
        const action = new URL(forms[0].action);
        expect(action.pathname).toContain('/login/geosecure/');
        expect(new FormData(forms[0]).get('next')).toBe(window.location.origin + '/request/?new_response=true&project=1#geosecure');
        expect(component.showNewUserMessage).toBe(true);
    });

    it('should only show the GeoPlatform form for GeoPlatform return URLs', () => {
        completeStartLogin();
        component.route.snapshot.queryParams.next = '/request/#geoplatform';
        component.checkQueryParams();
        fixture.detectChanges();

        const forms: HTMLFormElement[] = Array.from(fixture.nativeElement.querySelectorAll('form'));
        expect(forms.length).toBe(1);
        expect(forms[0].action).toContain('/login/geoplatform/');
    });

    it('should support login without a return URL', () => {
        completeStartLogin();
        delete component.route.snapshot.queryParams.next;
        component.checkQueryParams();
        fixture.detectChanges();

        const forms: HTMLFormElement[] = Array.from(fixture.nativeElement.querySelectorAll('form'));
        expect(forms.length).toBe(2);
        expect(new FormData(forms[0]).get('next')).toBe(window.location.origin);
    });
});
