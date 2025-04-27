// rating-modal/rating-modal.component.ts
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { MatDialogModule } from '@angular/material/dialog'

@Component({
  selector: 'app-rating-modal',
  templateUrl: './rating-modal.component.html',
  styleUrls: ['./rating-modal.component.css'],
  standalone: true,
  imports: [MatIconModule, CommonModule, MatDialogModule]
})
export class RatingModalComponent {
  selectedRating: number = 0;

  constructor(
    public dialogRef: MatDialogRef<RatingModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  setRating(rating: number): void {
    this.selectedRating = rating;
  }

  submitRating(): void {
    this.dialogRef.close(this.selectedRating);
  }
}