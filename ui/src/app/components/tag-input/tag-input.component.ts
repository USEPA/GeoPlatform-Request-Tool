import {Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import {FormControl, FormGroup} from '@angular/forms';
import {HttpClient} from '@angular/common/http';
import {COMMA, ENTER} from '@angular/cdk/keycodes';
import {Observable} from 'rxjs';
import {debounceTime, map, startWith, switchMap} from 'rxjs/operators';
import {isArray} from 'rxjs/internal-compatibility';

import {BaseService, Response} from '@services/base.service';
import {LoadingService} from '@services/loading.service';
import {MatAutocompleteSelectedEvent} from '@angular/material/autocomplete';
import {MatChipInputEvent} from '@angular/material/chips';

export interface TagItem {
  id: number;
  title: string;
}

@Component({
  selector: 'app-tag-input',
  templateUrl: './tag-input.component.html',
  styleUrls: ['./tag-input.component.css']
})
export class TagInputComponent implements OnInit {
  @Input() formControl: FormControl;
  @Input() tags: TagItem[];
  @Input() label: '';
  @Input() hint: '';

  tagsCtrl = new FormControl();
  filteredTags: Observable<TagItem[]>;
  tagsService: BaseService;
  allTags: Observable<Response>;
    // for tag autocomplete... all may not be needed
  separatorKeysCodes: number[] = [ENTER, COMMA];
  visible = true;
  selectable = true;
  removable = true;
  addOnBlur = false;

  @ViewChild('tagInput', {static: false}) tagInput: ElementRef;

  constructor(public http: HttpClient, public loadingService: LoadingService) {
    this.tagsService = new BaseService('v1/agol/groups/all', this.http, this.loadingService);
    this.allTags = this.tagsService.getList({all: true});
  }

  ngOnInit() {
    this.filteredTags = this.tagsCtrl.valueChanges.pipe(
      startWith(''),
      debounceTime(300),
      switchMap((tag: string | null) => {
        if (tag) {
          return this.tagsService.getList({search: tag});
        } else {
          return this.allTags;
        }
      }),
      map((response) => {
        if (isArray(response)) {
          if (this.tags && this.tags.length > 0) {
            return response.filter(result => this.tags.indexOf(result.title) === -1);
          }
          return response;
        }
      }),
    );
  }

  add(event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;

    if ((value || '').trim()) {
      this.tags.push({id: null, title: value.trim()});
    }

    // Reset the input value
    if (input) {
      input.value = '';
    }

    this.formControl.setValue(this.tags);
    this.tagsCtrl.setValue(null);
  }

  remove(tag: TagItem): void {
    const index = this.tags.indexOf(tag);

    if (index >= 0) {
      this.tags.splice(index, 1);
    }
    this.formControl.setValue(this.tags);
  }

  selected(event: MatAutocompleteSelectedEvent): void {
    if (this.tags && event.option.value) {
      this.tags.push({id: event.option.value.id, title: event.option.value.title});
    }
    this.tagInput.nativeElement.value = '';
    this.formControl.setValue(this.tags);
    this.tagsCtrl.setValue(null);
  }
}
