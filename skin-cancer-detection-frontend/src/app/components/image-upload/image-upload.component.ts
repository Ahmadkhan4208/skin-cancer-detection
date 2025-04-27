import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';
import { ResultsDisplayComponent } from '../results-display/results-display.component';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-image-upload',
  templateUrl: './image-upload.component.html',
  styleUrls: ['./image-upload.component.css'],
  standalone: true,
  imports: [
    MatButtonModule, 
    MatIconModule, 
    MatProgressSpinnerModule, 
    CommonModule,
    ResultsDisplayComponent
  ]
})
export class ImageUploadComponent {
  selectedFile: File | null = null;
  imagePreview: string | ArrayBuffer | null = null;
  isDragging = false;
  isLoading = false;
  showResults = false;
  analysisResults: any = null;

  constructor(
    private apiService: ApiService,
    private snackBar: MatSnackBar,
    private authService: AuthService,
  ) { }

  ngOnInit(): void {}

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    this.handleFile(file);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
    
    const file = event.dataTransfer?.files[0];
    if (file) {
      this.handleFile(file);
    }
  }

  handleFile(file: File): void {
    if (!file.type.match('image.*')) {
      this.snackBar.open('Please upload an image file', 'Close', { duration: 3000 });
      return;
    }

    this.selectedFile = file;

    const reader = new FileReader();
    reader.onload = () => {
      this.imagePreview = reader.result;
    };
    reader.readAsDataURL(file);
  }

  removeImage(event: Event): void {
    event.stopPropagation();
    this.selectedFile = null;
    this.imagePreview = null;
  }

  analyze(): void {
    if (!this.selectedFile) return;
  
    this.isLoading = true;
    this.showResults = false;
    const userId = this.authService.getCurrentUserId();
    this.apiService.analyzeImage(this.selectedFile,userId).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.showResults = true;
        this.analysisResults = {
          predicted_class: response.predicted_class,
          confidence: response.confidence,
          conclusion: response.conclusion,
          description: response.description
        };
      },
      error: (error) => {
        this.isLoading = false;
        console.error('API Error:', error);
        if (error.status === 422) {
          this.snackBar.open('Invalid file format or upload error', 'Close', { duration: 3000 });
        } else {
          this.snackBar.open('Server error. Please try again.', 'Close', { duration: 3000 });
        }
      },
      complete: () => {
        this.isLoading = false;
      }
    });
  }

  resetUpload(): void {
    this.selectedFile = null;
    this.imagePreview = null;
    this.showResults = false;
    this.analysisResults = null;
    
    // Reset the file input to allow re-uploading the same file
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }
}
