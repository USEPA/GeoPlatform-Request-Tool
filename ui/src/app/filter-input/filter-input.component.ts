import {Component, EventEmitter, Output, Input} from '@angular/core';

@Component({
  selector: 'filter-input',
  templateUrl: './filter-input.component.html',
  styleUrls: ['./filter-input.component.css']
})
export class FilterInputComponent {
  @Input() label: string;
  @Input() type: string;
  @Input() field_name: string;
  @Output() filterCleared: EventEmitter<string> = new EventEmitter<string>();
  @Input() filtered: boolean;
  @Output() filteredChange: EventEmitter<any> = new EventEmitter<any>();
  @Input() choices: object[];
  @Input() value_field: string;

  clearFilter(event) {
    event.stopPropagation();
    delete this.filtered;
    this.filterCleared.emit();
  }

}
