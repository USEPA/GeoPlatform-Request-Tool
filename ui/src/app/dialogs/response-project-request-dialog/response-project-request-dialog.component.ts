import { Component, OnInit } from '@angular/core';
import {MatDialogRef} from '@angular/material/dialog';

@Component({
  selector: 'app-response-project-request-dialog',
  templateUrl: './response-project-request-dialog.component.html',
  styleUrls: ['./response-project-request-dialog.component.css']
})
export class ResponseProjectRequestDialogComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<ResponseProjectRequestDialogComponent>) { }

  ngOnInit(): void {
  }

}
