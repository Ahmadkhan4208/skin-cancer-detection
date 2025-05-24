import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { RouterModule } from '@angular/router';
import { PredictionService, PredictionHistory } from '../../services/prediction.service';
import { environment } from '../../../environments/environment';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-prediction-history',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatDividerModule,
    RouterModule,
    HttpClientModule
  ],
  providers: [PredictionService],
  templateUrl: './prediction-history.html',
  styleUrls: ['./prediction-history.css']
})
export class PredictionHistoryComponent implements OnInit {
  predictions: PredictionHistory[] = [];
  baseUrl = environment.apiUrl;
  isLoading = true;
  error: string | null = null;

  constructor(private predictionService: PredictionService) { }

  ngOnInit(): void {
    this.loadPredictionHistory();
  }

  loadPredictionHistory(): void {
    this.isLoading = true;
    this.predictionService.getPredictionHistory().subscribe({
      next: (data) => {
        this.predictions = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load prediction history';
        this.isLoading = false;
      }
    });
  }

  getFormattedDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString();
  }

  getImageUrl(imagePath: string): string {
    if (imagePath.startsWith('http')) {
        return imagePath;
    }
    
    // Extract the filename from the path
    const filename = imagePath.split('/').pop();
    
    // Use the correct path to the images directory
    return `${this.baseUrl}/static/uploads/${filename}`;
    }

  getStatusClass(conclusion: string): string {
    if (conclusion.includes('Benign')) {
      return 'benign';
    } else if (conclusion.includes('malignancy')) {
      return 'malignant';
    } else {
      return 'uncertain';
    }
  }
  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}