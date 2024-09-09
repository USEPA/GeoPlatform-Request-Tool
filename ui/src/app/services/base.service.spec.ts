import {TestBed, inject} from '@angular/core/testing';

import {BaseService} from './base.service';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {B} from '@angular/cdk/keycodes';
import {HttpClient} from '@angular/common/http';
import {LoadingService} from '@services/loading.service';

let service: BaseService;

describe('BaseService', () => {

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = new BaseService('', {} as HttpClient, {} as LoadingService)
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
