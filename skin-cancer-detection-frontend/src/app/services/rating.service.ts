// rating.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RatingService {
  private apiUrl = environment.apiUrl + '/api/ratings';

  constructor(private http: HttpClient) { }

  // Submit a rating for an appointment
  submitRating(appointment_id: number, rating: number): Observable<number> {
    return this.http.post<number>(`${this.apiUrl}/set_rating`, { appointment_id, rating });
  }

  // Check if a patient has already rated an appointment
  hasRated(appointmentId: number): Observable<boolean> {
    // Validate input
    if (!appointmentId || isNaN(appointmentId)) {
      return throwError(() => new Error('Invalid appointment ID'));
    }
  
    return this.http.get<boolean>(`${this.apiUrl}/has_rated`, {
      params: { appointment_id: appointmentId }
    }).pipe(
      catchError(error => {
        console.error('Error checking rating status:', error);
        return of(false); // Default to false if there's an error
      })
    );
  }
}


