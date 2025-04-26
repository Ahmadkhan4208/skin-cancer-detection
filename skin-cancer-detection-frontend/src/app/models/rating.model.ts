// rating.model.ts
export interface RatingBase {
    appointment_id: number;
    doctor_id: number;
    patient_id: number;
    rating: number;
    comment?: string;
  }
  
  export interface RatingCreate extends RatingBase {
    // Additional fields if needed
  }
  
  export interface Rating extends RatingBase {
    id: number;
    created_at: Date;
    // Add any additional fields from backend
  }