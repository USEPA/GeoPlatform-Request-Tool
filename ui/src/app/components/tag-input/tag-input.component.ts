import {Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild, ChangeDetectionStrategy} from '@angular/core';
import {FormGroup, FormControl, ReactiveFormsModule} from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import {COMMA, ENTER} from '@angular/cdk/keycodes';
import {Observable, debounceTime} from 'rxjs';
import {map, startWith, switchMap} from 'rxjs/operators';
// import {isArray} from 'rxjs/internal-compatibility';

import {BaseService, Response} from '@services/base.service';
import {LoadingService} from '@services/loading.service';
import {
  MatAutocomplete,
  MatAutocompleteSelectedEvent, MatAutocompleteTrigger, MatOption
} from '@angular/material/autocomplete';
import {MatChipGrid, MatChipInput, MatChipInputEvent, MatChipRow} from '@angular/material/chips';
import {MatFormField, MatHint, MatLabel} from "@angular/material/input";
import {MatIcon} from "@angular/material/icon";
import {AsyncPipe} from "@angular/common";

export interface TagItem {
  id: number | null;
  title: string;
}

@Component({
  selector: 'app-tag-input',
  templateUrl: './tag-input.component.html',
  styleUrls: ['./tag-input.component.css'],
  changeDetection: ChangeDetectionStrategy.Eager,
  imports: [
    MatFormField,
    MatLabel,
    MatChipGrid,
    MatChipRow,
    MatIcon,
    ReactiveFormsModule,
    MatAutocompleteTrigger,
    MatChipInput,
    MatAutocomplete,
    MatOption,
    AsyncPipe,
    MatHint
  ]
})
export class TagInputComponent implements OnInit {
  @Output() tagSelected: EventEmitter<number[]> = new EventEmitter<number[]>();
  @Input() tags!: TagItem[];
  @Input() label!: string;
  @Input() hint!: string;
  @Input() tagsService!: BaseService;

  tagsCtrl = new FormControl<string>('');
  filteredTags!: Observable<any[]>;
  allTags!: Observable<any[]>;
  // for tag autocomplete... all may not be needed
  separatorKeysCodes: number[] = [ENTER, COMMA];
  visible = true;
  selectable = true;
  removable = true;
  addOnBlur = false;

  @ViewChild('tagInput', {static: false}) tagInput!: ElementRef;

  constructor(public http: HttpClient, public loadingService: LoadingService) {
  }

  ngOnInit() {
    this.allTags = this.tagsService.getList().pipe(map((r: Response) => r.results));
    this.listenToTags();
  }

  listenToTags() {
    this.filteredTags = this.tagsCtrl.valueChanges.pipe(
      startWith(''),
      debounceTime(300),
      switchMap((tag: string | null) => {
        if (tag) {
          return this.tagsService.getList({search: tag, page: 1}).pipe(map(r => r.results));
        } else {
          return this.allTags;
        }
      })
    );
  }

  add(event: MatChipInputEvent): void {
    const input = event.chipInput.inputElement;
    const value = event.value;

    if ((value || '').trim()) {
      this.tags.push({id: null, title: value.trim()});
    }

    // Reset the input value
    if (input) {
      input.value = '';
    }

    this.emitSelectedTags();
    this.tagsCtrl.setValue(null);
  }

  remove(tag: TagItem): void {
    const index = this.tags.indexOf(tag);

    if (index >= 0) {
      this.tags.splice(index, 1);
    }
    this.emitSelectedTags();
  }

  selected(event: MatAutocompleteSelectedEvent): void {
    if (this.tags && event.option.value) {
      this.tags.push({id: event.option.value.id, title: event.option.value.title});
    }
    this.tagInput.nativeElement.value = '';
    this.emitSelectedTags();
    this.tagsCtrl.setValue(null);
  }

  private emitSelectedTags(): void {
    this.tagSelected.emit(this.tags.filter(x => x.id !== null).map(x => x.id) as number[]);
  }
}
