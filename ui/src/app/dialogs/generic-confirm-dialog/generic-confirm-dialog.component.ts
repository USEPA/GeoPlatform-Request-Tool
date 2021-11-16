import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';

@Component({
  selector: 'app-generic-confirm-dialog',
  templateUrl: './generic-confirm-dialog.component.html',
  styleUrls: ['./generic-confirm-dialog.component.css']
})
export class GenericConfirmDialogComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<GenericConfirmDialogComponent>,
              @Inject(MAT_DIALOG_DATA) public data) { }

  ngOnInit(): void {
  }

}
