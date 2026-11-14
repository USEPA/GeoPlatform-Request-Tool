import { beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TagInputComponent } from './tag-input.component';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { LoadingService } from '@services/loading.service';
import { BaseService } from '@services/base.service';
import { Observable } from 'rxjs';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';

describe('TagInputComponent', () => {
    let component: TagInputComponent;
    let fixture: ComponentFixture<TagInputComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [TagInputComponent],
            providers: [
                { provide: LoadingService, useValue: {} },
                provideHttpClient(withXhr(), withInterceptorsFromDi()),
                provideHttpClientTesting()
            ]
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(TagInputComponent);
        component = fixture.componentInstance;
        component.tagsService = { getList: () => new Observable() } as BaseService;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
