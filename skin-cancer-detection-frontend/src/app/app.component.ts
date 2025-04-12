import { Component } from '@angular/core';
import { ImageUploadComponent } from './components/image-upload/image-upload.component';
import { ResultsDisplayComponent } from './components/results-display/results-display.component';
import { CommonModule } from '@angular/common';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [ImageUploadComponent, ResultsDisplayComponent, CommonModule]
})
export class AppComponent {
  results: any = null;

  resetUpload(): void {
    this.results = null;
  }

  // You'll want to connect this to the actual results from the API
  // This is just a placeholder for the structure
  onAnalysisComplete(results: any): void {
    this.results = results;
  }
}