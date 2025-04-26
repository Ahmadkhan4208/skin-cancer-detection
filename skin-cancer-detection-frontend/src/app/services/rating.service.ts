// rating.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Rating, RatingCreate } from '../models/rating.model';

@Injectable({
  providedIn: 'root'
})
export class RatingService {
  private apiUrl = 'http://your-api-url/api/ratings';

  constructor(private http: HttpClient) { }

  // Submit a rating for an appointment
  submitRating(rating: RatingCreate): Observable<Rating> {
    return this.http.post<Rating>(this.apiUrl, rating);
  }

  // Check if a patient has already rated an appointment
  hasRated(appointmentId: number): Observable<boolean> {
    return this.http.get<boolean>(`${this.apiUrl}/has_rated?appointment_id=${appointmentId}`);
  }

  // Get all ratings for a doctor
  getDoctorRatings(doctorId: number): Observable<Rating[]> {
    return this.http.get<Rating[]>(`${this.apiUrl}?doctor_id=${doctorId}`);
  }

  // Update a rating
  updateRating(ratingId: number, updates: Partial<Rating>): Observable<Rating> {
    return this.http.patch<Rating>(`${this.apiUrl}/${ratingId}`, updates);
  }
}