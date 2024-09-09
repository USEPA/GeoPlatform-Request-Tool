import { TestBed, async } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { AppComponent } from './app.component';
import {LoadingService} from '@services/loading.service';
import {LoginService} from './auth/login.service';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatIconModule} from '@angular/material/icon';
import {MatLegacySnackBarModule} from '@angular/material/legacy-snack-bar';

describe('AppComponent', () => {
  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
        HttpClientTestingModule,
        MatToolbarModule,
        MatIconModule,
        MatLegacySnackBarModule
      ],
      declarations: [
        AppComponent
      ],
      providers: [
        {provide: LoadingService, useValue: {}},
        {provide: LoginService, useValue: {}}
      ]
    }).compileComponents();
  }));

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  });

});
