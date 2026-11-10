import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {LoginComponent} from './login.component';
import {AuthModule} from '../auth.module';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {RouterTestingModule} from '@angular/router/testing';
import {ActivatedRoute} from '@angular/router';
import {HttpXsrfTokenExtractor} from '@angular/common/http';
import {environment} from '../../../environments/environment';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        AuthModule,
        HttpClientTestingModule,
        RouterTestingModule
      ],
      providers: [
        {
          provide: HttpXsrfTokenExtractor,
          useValue: {getToken: () => 'test-csrf-token'}
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
        }
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render native POST forms for both providers with CSRF tokens', () => {
    const forms: HTMLFormElement[] = Array.from(fixture.nativeElement.querySelectorAll('form'));
    expect(forms.length).toBe(2);
    forms.forEach((form, index) => {
      const provider = index === 0 ? 'geoplatform' : 'geosecure';
      expect(form.method).toBe('post');
      expect(form.getAttribute('action')).toBe(
        `${environment.oauth_url}/login/${provider}/`
      );
      expect(new FormData(form).get('next')).toBe(window.location.origin + 'test');
      expect(form.querySelector('button').type).toBe('submit');
      expect((form.elements.namedItem('csrfmiddlewaretoken') as HTMLInputElement).value).toBe('test-csrf-token');
      const event = new Event('submit', {bubbles: true, cancelable: true});
      form.dispatchEvent(event);
      expect(event.defaultPrevented).toBeFalse();
    });
  });

  it('should preserve the entire return URL including query parameters and fragments', () => {
    component.route.snapshot.queryParams.next = '/request/?new_response=true&project=1#geosecure';
    component.checkQueryParams();
    fixture.detectChanges();

    const forms: HTMLFormElement[] = Array.from(fixture.nativeElement.querySelectorAll('form'));
    expect(forms.length).toBe(1);
    const action = new URL(forms[0].action);
    expect(action.pathname).toContain('/login/geosecure/');
    expect(new FormData(forms[0]).get('next')).toBe(
      window.location.origin + '/request/?new_response=true&project=1#geosecure'
    );
    expect(component.showNewUserMessage).toBeTrue();
  });

  it('should only show the GeoPlatform form for GeoPlatform return URLs', () => {
    component.route.snapshot.queryParams.next = '/request/#geoplatform';
    component.checkQueryParams();
    fixture.detectChanges();

    const forms: HTMLFormElement[] = Array.from(fixture.nativeElement.querySelectorAll('form'));
    expect(forms.length).toBe(1);
    expect(forms[0].action).toContain('/login/geoplatform/');
  });

  it('should support login without a return URL', () => {
    delete component.route.snapshot.queryParams.next;
    component.checkQueryParams();
    fixture.detectChanges();

    const forms: HTMLFormElement[] = Array.from(fixture.nativeElement.querySelectorAll('form'));
    expect(forms.length).toBe(2);
    expect(new FormData(forms[0]).get('next')).toBe(window.location.origin);
  });
});
