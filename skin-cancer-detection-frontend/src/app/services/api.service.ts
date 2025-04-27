import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  analyzeImage(imageFile: File, userId: any): Observable<any> {
    console.log('Uploading file:', imageFile.name, imageFile.type, imageFile.size);
  
    const formData = new FormData();
    formData.append('image', imageFile, imageFile.name);  // Image
    formData.append('user_id', userId.toString());        // User ID also
  
    return this.http.post(`${this.apiUrl}/analyze`, formData, {
      headers: this.getHeaders(),
      reportProgress: true
    });
  }
  
}