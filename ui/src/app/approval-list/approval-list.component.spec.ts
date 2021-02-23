import {getTestBed, TestBed, tick} from '@angular/core/testing';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {HttpClient, HttpXhrBackend} from '@angular/common/http';

import {environment} from '@environments/environment';
import { ApprovalListComponent } from './approval-list.component';
import {BaseService} from '@services/base.service';
import {LoadingService} from '@services/loading.service';


describe('ApprovalListComponent', () => {
  let component: ApprovalListComponent;
  const http: HttpClient = new HttpClient(new HttpXhrBackend({ build: () => new XMLHttpRequest() }));
  const loadingService: LoadingService = new LoadingService();

  beforeEach(() => {
    component = new ApprovalListComponent(http, loadingService);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

describe('ApprovalApiService', () => {
  let injector: TestBed;
  const http: HttpClient = new HttpClient(new HttpXhrBackend({ build: () => new XMLHttpRequest() }));
  const loadingService: LoadingService = new LoadingService();
  const endpoint = 'v1/account/approvals/approve';
  // const service: BaseService = new BaseService('v1/account/approvals/approve', http, loadingService);
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    });
    injector = getTestBed();
    httpMock = injector.get(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should return an Observable<string>', () => {
    const expectedResponse = 'Accounts created. Existing account NOT updated.';

    const body = {
      accounts: [1, 2],
      password: 'mock password'
    };
    const url = `${environment.local_test_service_endpoint}/${endpoint}`;
    http.post(url, body).subscribe(resp => {
      expect(resp).toEqual(expectedResponse);
    });

    const req = httpMock.expectOne(url);
    expect(req.request.method).toBe('POST');
    expect(req.request.url).toBe(url);
    expect(req.request.body).toEqual(body);

    req.flush(body);
    httpMock.verify();
    tick(); // blocks execution and waits for all the pending promises to be resolved.
  });
});
