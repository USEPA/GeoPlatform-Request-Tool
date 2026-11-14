import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import {MatDialogContent, MatDialogRef, MatDialogTitle} from '@angular/material/dialog';
import {
  FieldCoordErRequestFormComponent
} from "../../field-coord-er-request-form/field-coord-er-request-form.component";

@Component({
  selector: 'app-response-project-request-dialog',
  templateUrl: './response-project-request-dialog.component.html',
  styleUrls: ['./response-project-request-dialog.component.css'],
  changeDetection: ChangeDetectionStrategy.Eager,
  imports: [
    MatDialogContent,
    FieldCoordErRequestFormComponent,
    MatDialogTitle
  ]
})
export class ResponseProjectRequestDialogComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<ResponseProjectRequestDialogComponent>) { }

  ngOnInit(): void {
  }

}
