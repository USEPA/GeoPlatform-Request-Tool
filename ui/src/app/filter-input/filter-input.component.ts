import {Component, EventEmitter, Output, Input, ChangeDetectionStrategy} from '@angular/core';

@Component({
    selector: 'filter-input',
    templateUrl: './filter-input.component.html',
    styleUrls: ['./filter-input.component.css'],
    changeDetection: ChangeDetectionStrategy.Eager,
    standalone: false
})
export class FilterInputComponent {
  @Input() label!: string;
  @Input() type!: string;
  @Input() field_name!: string;
  @Output() filterCleared: EventEmitter<string> = new EventEmitter<string>();
  @Input() filtered?: boolean;
  @Output() filteredChange: EventEmitter<any> = new EventEmitter<any>();
  @Input() choices!: object[];
  @Input() value_field!: string;

  clearFilter(event: Event) {
    event.stopPropagation();
    delete this.filtered;
    this.filterCleared.emit();
  }

}
