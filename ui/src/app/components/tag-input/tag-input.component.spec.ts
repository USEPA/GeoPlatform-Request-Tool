import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {TagInputComponent} from './tag-input.component';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {LoadingService} from '@services/loading.service';
import {MatLegacyAutocompleteModule as MatAutocompleteModule} from '@angular/material/legacy-autocomplete';
import {MatLegacyInputModule} from '@angular/material/legacy-input';
import {MatLegacyChipsModule} from '@angular/material/legacy-chips';
import {MatLegacyFormFieldModule} from '@angular/material/legacy-form-field';
import {NoopAnimationsModule} from '@angular/platform-browser/animations';

describe('TagInputComponent', () => {
  let component: TagInputComponent;
  let fixture: ComponentFixture<TagInputComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [TagInputComponent],
      imports: [
        MatAutocompleteModule,
        HttpClientTestingModule,
        MatLegacyFormFieldModule,
        MatLegacyChipsModule,
        MatLegacyInputModule,
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
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
