// appointment.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Appointment, AppointmentCreate } from '../models/appointment.model';

@Injectable({
  providedIn: 'root'
})
export class AppointmentService {
    private apiUrl = environment.apiUrl + "/appointments";

  constructor(private http: HttpClient) { }

  // Create a new appointment
  createAppointment(appointment: AppointmentCreate): Observable<Appointment> {
    return this.http.post<Appointment>(this.apiUrl, appointment);
  }

  // Get appointments between a specific patient and doctor
  getPatientDoctorAppointments(patientId: number, doctorId: number): Observable<Appointment[]> {
    return this.http.get<Appointment[]>(
      `${this.apiUrl}?patient_id=${patientId}&doctor_id=${doctorId}`
    );
  }

  // Get all appointments for current patient
  getPatientAppointments(patientId: number): Observable<Appointment[]> {
    return this.http.get<Appointment[]>(`${this.apiUrl}?patient_id=${patientId}`);
  }

  // Update an appointment
  updateAppointment(id: number, updates: Partial<Appointment>): Observable<Appointment> {
    return this.http.patch<Appointment>(`${this.apiUrl}/${id}`, updates);
  }

  // Cancel an appointment
  cancelAppointment(id: number): Observable<Appointment> {
    return this.http.patch<Appointment>(`${this.apiUrl}/${id}/cancel`, {});
  }
}