import { beforeEach, describe, expect, it } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FilterInputComponent } from './filter-input.component';
import {MatFormField, MatLabel} from "@angular/material/input";
import {MatSelect} from "@angular/material/select";
import {FormsModule, NgModel, ReactiveFormsModule} from "@angular/forms";

describe('FilterInputComponent', () => {
    let component: FilterInputComponent;
    let fixture: ComponentFixture<FilterInputComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [FilterInputComponent],
          imports: [MatFormField, MatLabel, MatSelect, ReactiveFormsModule, FormsModule ]
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(FilterInputComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
