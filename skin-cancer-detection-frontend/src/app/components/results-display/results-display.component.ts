import { Component, Input, Output, EventEmitter } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-results-display',
  templateUrl: './results-display.component.html',
  styleUrls: ['./results-display.component.css'],
  standalone: true,
  imports: [MatIconModule, MatButtonModule, CommonModule]
})
export class ResultsDisplayComponent {
  @Input() results: any;
  @Output() newUpload = new EventEmitter<void>();

  get lesionType(): string {
    // Map the predicted_class to more readable format
    const types: {[key: string]: string} = {
      'nv': 'Melanocytic nevus',
      'mel': 'Melanoma',
      'bkl': 'Benign keratosis-like lesion',
      'bcc': 'Basal cell carcinoma',
      'akiec': 'Actinic keratosis',
      'vasc': 'Vascular lesion',
      'df': 'Dermatofibroma'
    };
    return types[this.results?.predicted_class] || this.results?.predicted_class || 'Unknown';
  }

  uploadNew(): void {
    this.newUpload.emit();
  }
}