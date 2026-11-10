import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FieldCoordErRequestFormComponent } from './field-coord-er-request-form.component';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {LoadingService} from '@services/loading.service';

describe('FieldCoordErRequestFormComponent', () => {
  let component: FieldCoordErRequestFormComponent;
  let fixture: ComponentFixture<FieldCoordErRequestFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FieldCoordErRequestFormComponent ],
      imports: [HttpClientTestingModule, MatSnackBarModule],
      providers: [
        {provide: LoadingService, useValue: {}}
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FieldCoordErRequestFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
