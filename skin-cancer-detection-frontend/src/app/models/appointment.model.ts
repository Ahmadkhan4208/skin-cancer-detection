// appointment.model.ts
export interface AppointmentBase {
    patient_id: number;
    doctor_id: number;
    date_time: string;
    notes?: string;
  }
  
  export interface AppointmentCreate extends AppointmentBase {
    // Additional fields if needed
  }
  
  export interface Appointment extends AppointmentBase {
    appointment_id: number;
    patient_id: number;
    status: 'pending' | 'book' | 'rate';
    doctor: Doctor;
    patient: Patient;
  }
  
  export interface Doctor {
    id: number;
    user_name: string;
    specialty: string;
    hospital: string;
    years_experience: number;
    contact: string;
    rating?: number;
    profile_image_url: string;
    email?: string; // Added from Users table
  }
  
  export interface Patient {
    id: number;
    user_name: string;
    // Add other patient fields as needed
  }