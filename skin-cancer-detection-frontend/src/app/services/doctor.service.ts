import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DoctorService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getAllDoctors(): Observable<any> {
    return this.http.get(`${this.apiUrl}/doctors`);  // Make sure the endpoint matches
  }
}
