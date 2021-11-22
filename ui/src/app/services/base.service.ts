import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from "@angular/common/http";
import {Observable, BehaviorSubject, ReplaySubject} from "rxjs";
import {LoadingService} from "./loading.service";
import {DataSource} from "@angular/cdk/collections";
import {map, tap} from 'rxjs/operators';

export interface SearchObject {
  search?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
  object_id?: string | number;
  content_type?: any;
  approved_and_created?: boolean;
  created?: boolean;
  approved?: boolean;

  [key: string]: any;
}

export interface Response {
  count: number;
  results: any[];
  content_type?: number;
}

export class BaseService {
  currentPage: number;
  count: number;
  dataChange: BehaviorSubject<any[]> = new BehaviorSubject<any[]>([]);
  filter: SearchObject;
  datasource: BaseDataSource;
  content_type = new ReplaySubject();

  constructor(public base_url: string, public http: HttpClient, public loadingService: LoadingService) {
    this.datasource = new BaseDataSource(this);
    this.filter = {};
  }

  get data(): any[] {
    return this.dataChange.value;
  }

  getList<Any>(search_object: SearchObject = {}): Observable<Response> {
    let url = `/${this.base_url}/`;
    return this.http.get<Response>(url,
      {
        params: Object.entries(search_object).reduce((params, [key, value]) => params.set(key, value), new HttpParams())
      }
    ).pipe(
      map(response => {
        if (response.hasOwnProperty('content_type')) {
          this.content_type.next(response.content_type);
          this.content_type.complete();
        }
        return response;
      })
    );
  }

  get(id: string | number) {
    return this.http.get<any>(`/${this.base_url}/${id}/`);
  }

  put(id: string | number, item: object) {
    return this.http.put(`/${this.base_url}/${id}/`, item);
  }

  post(item: object, httpOptions = {}): any {
    return this.http.post(`/${this.base_url}/`, item, httpOptions).pipe(
      map(item => {
        const copiedData = this.data.slice();
        copiedData.push(item);
        this.dataChange.next(copiedData);
        return item;
      })
    );
  }

  options() {
    return this.http.options<any>(`/${this.base_url}/`);
  }

  getItems(): Observable<any[]> {
    this.loadingService.setLoading(true);
    return this.getList(this.filter).pipe(
      map(response => {
        this.currentPage = this.filter.page;
        this.count = response.count;
        this.dataChange.next(response.results);
        this.loadingService.setLoading(false);
        return response.results;
      })
    );
  }

  getPage(event) {
    this.loadingService.setLoading(true);
    this.filter.page = event.pageIndex + 1;
    this.filter.page_size = event.pageSize;
    this.getItems()
      .subscribe(() => this.loadingService.setLoading(false));
  }

  runSearch() {
    this.loadingService.setLoading(true);
    this.filter.page = 1;
    this.getItems()
      .subscribe(() => this.loadingService.setLoading(false));
  }

  clearSearch() {
    this.loadingService.setLoading(true);
    this.filter.search = '';
    this.getItems().subscribe(() => this.loadingService.setLoading(false));
  }

  clearFilter(field) {
    delete this.filter[field];
  }

  clearAllFilters() {
    for (let key in this.filter) {
      if (key !== 'page' && key !== 'page_size' && key !== 'search') {
        delete this.filter[key];
      }
    }
    this.getItems().subscribe();
  }

  sortTable(event) {
    // this.loadingService.setLoading(true);
    this.filter.page = 1;
    let direction = event.direction === 'desc' ? '-' : '';
    this.filter.ordering = event.direction ? `${direction}${event.active}` : '';
    this.getItems()
      .subscribe(() => this.loadingService.setLoading(false));
  }

  delete(id: string | number) {
    return this.http.delete(`/${this.base_url}/${id}/`)
      .pipe(
        map(() => {
          const copiedData = this.data.slice();
          const filteredData = copiedData.filter(item => item.id !== id);
          this.dataChange.next(filteredData);
        })
      );
  }

}

export class BaseDataSource extends DataSource<any> {
  constructor(private _projectDatabase: BaseService) {
    super();
  }

  connect(): Observable<any[]> {
    return this._projectDatabase.dataChange;
  }

  disconnect() {
  }
}
