import { OnInit } from '@angular/core';
import { Component, Input } from '@angular/core';
import { AppointmentService } from '../../services/appointment.service';
import { Appointment } from '../../models/appointment.model';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-doctor-appointments-cards',
  templateUrl: './doctor-appointments-cards.component.html',
  styleUrls: ['./doctor-appointments-cards.component.scss'],
  standalone: true,
  imports: [CommonModule, MatIconModule]
})
export class DoctorAppointmentsCardsComponent implements OnInit {
  appointments: Appointment[] = [];

  constructor(private appointmentService: AppointmentService,
    private route: ActivatedRoute,
    private authService: AuthService 
  ) {}

  ngOnInit(): void {
    this.fetchAppointments();
  }

  fetchAppointments(): void {
    const doctorId = this.authService.getCurrentUserId() || 0;
    this.appointmentService.getDoctorAppointments(doctorId).subscribe((data) => {
      this.appointments = data;
    });
  }

  confirmAppointment(appointmentId: number): void {
    this.appointmentService.updateAppointmentStatus(appointmentId, "book").subscribe(() => {
      this.fetchAppointments(); // Refresh the appointments after confirming
    });
  }
}