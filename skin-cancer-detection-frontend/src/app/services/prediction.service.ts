import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface PredictionHistory {
  id: number;
  user_id: number;
  image_path: string;
  predicted_class: string;
  predicted_at: string;
  confidence: number;
  conclusion: string;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class PredictionService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getPredictionHistory(): Observable<PredictionHistory[]> {
    return this.http.get<PredictionHistory[]>(`${this.apiUrl}/prediction-history`);
  }

    getPredictionById(id: number): Observable<PredictionHistory> {
    return this.http.get<PredictionHistory>(`${this.apiUrl}/prediction/${id}`);
    }
}