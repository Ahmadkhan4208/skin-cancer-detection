import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }


  completeProfile(
    userId: number, 
    profileData: any, 
    role: string,
    profileImage?: File
  ): Observable<any> {
    const formData = new FormData();
  
    // Append each field explicitly
    if (role === 'doctor') {
      formData.append('user_name', profileData.user_name);
      formData.append('specialty', profileData.specialty);
      formData.append('hospital', profileData.hospital);
      formData.append('years_experience', profileData.years_experience.toString());
    }
  
    formData.append('contact', profileData.contact);
  
    // Append the image if it exists
    if (profileImage) {
      formData.append('profile_image', profileImage, profileImage.name);
    }
  
    return this.http.post(
      `${this.apiUrl}/complete-profile/${userId}`,
      formData,
      { params: { role } }
    );
  }
  
  
  getDoctorProfile(userId: number): Observable<any> {
    return this.http.get(
        `${this.apiUrl}/doctordetails/${userId}`
    )
  }
}