import {Component, Inject, OnInit} from '@angular/core';
import {MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA, MatLegacyDialogRef as MatDialogRef} from '@angular/material/legacy-dialog';

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
