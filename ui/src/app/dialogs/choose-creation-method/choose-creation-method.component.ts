import { Component, OnInit } from '@angular/core';
import {MatDialogRef} from '@angular/material/dialog';

@Component({
  selector: 'app-choose-creation-method',
  templateUrl: './choose-creation-method.component.html',
  styleUrls: ['./choose-creation-method.component.css']
})
export class ChooseCreationMethodComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<ChooseCreationMethodComponent>) { }

  ngOnInit() {
  }

}
