import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {TagInputComponent} from './tag-input.component';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {LoadingService} from '@services/loading.service';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatInputModule} from '@angular/material/input';
import {MatChipsModule} from '@angular/material/chips';
import {MatFormFieldModule} from '@angular/material/form-field';
import {NoopAnimationsModule} from '@angular/platform-browser/animations';
import {BaseService} from '@services/base.service';
import {Observable} from 'rxjs';

describe('TagInputComponent', () => {
  let component: TagInputComponent;
  let fixture: ComponentFixture<TagInputComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [TagInputComponent],
      imports: [
        MatAutocompleteModule,
        HttpClientTestingModule,
        MatFormFieldModule,
        MatChipsModule,
        MatInputModule,
        NoopAnimationsModule
      ],
      providers: [
        {provide: LoadingService, useValue: {}}
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TagInputComponent);
    component = fixture.componentInstance;
    component.tagsService = {getList: () => new Observable()} as BaseService
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
