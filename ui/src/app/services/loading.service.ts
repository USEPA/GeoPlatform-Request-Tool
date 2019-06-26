import { Injectable } from '@angular/core';
import {Subject} from 'rxjs';

@Injectable()
export class LoadingService {
  public loadingStream: Subject<boolean> = new Subject();
  constructor() { }

  public setLoading(value: boolean) {
    this.loadingStream.next(value);
  }

  public getLoadingStream () {
    return this.loadingStream;
  }
}
