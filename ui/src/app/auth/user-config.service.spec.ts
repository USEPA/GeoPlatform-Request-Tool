import { TestBed } from '@angular/core/testing';

import { UserConfigService } from './user-config.service';
import {HttpClientTestingModule} from '@angular/common/http/testing';

describe('UserConfigService', () => {
  beforeEach(() => TestBed.configureTestingModule({
    imports: [
      HttpClientTestingModule
    ]
  }));

  it('should be created', () => {
    const service: UserConfigService = TestBed.get(UserConfigService);
    expect(service).toBeTruthy();
  });
});
