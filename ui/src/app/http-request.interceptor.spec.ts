import { TestBed, inject } from '@angular/core/testing';
import {HttpRequestInterceptor} from './http-request.interceptor';



describe('HttpRequestInterceptor', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [HttpRequestInterceptor]
    });
  });

  it('should be created', inject([HttpRequestInterceptor], (service: HttpRequestInterceptor) => {
    expect(service).toBeTruthy();
  }));
});
