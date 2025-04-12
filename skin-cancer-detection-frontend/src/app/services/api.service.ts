import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // api.service.ts
analyzeImage(imageFile: File): Observable<any> {
  console.log('Uploading file:', imageFile.name, imageFile.type, imageFile.size); // Debug
  
  const formData = new FormData();
  formData.append('image', imageFile, imageFile.name); // Added filename as 3rd param
  
  return this.http.post(`${this.apiUrl}/analyze`, formData, {
    reportProgress: true // Optional: track upload progress
  });
}
}