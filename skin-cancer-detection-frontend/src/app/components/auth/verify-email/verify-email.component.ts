import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatDialogModule } from '@angular/material/dialog';
import { AuthService } from '../../../services/auth.service'; // Add this import
import { MatSnackBar } from '@angular/material/snack-bar'; // For error messages

@Component({
  selector: 'app-verify-email',
  templateUrl: './verify-email.component.html',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDialogModule
  ]
})
export class VerifyEmailComponent {
  verifyForm: FormGroup;
  isLoading = false;
  countdown = 60;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<VerifyEmailComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { email: string },
    private authService: AuthService, // Inject AuthService
    private snackBar: MatSnackBar // For showing errors
  ) {
    this.verifyForm = this.fb.group({
      code: ['', [Validators.required, Validators.minLength(6)]]
    });
    this.startCountdown();
  }

  onSubmit() {
    if (this.verifyForm.invalid) return;
    this.isLoading = true;
    
    this.authService.verifyCode(this.data.email, this.verifyForm.value.code).subscribe({
      next: (response) => {
        this.isLoading = false;
        if (response.verified) {
          this.dialogRef.close(true); // Close dialog with success
        } else {
          this.snackBar.open('Invalid verification code', 'Close', { 
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open(
          error.error?.message || 'Verification failed', 
          'Close', 
          { duration: 3000 }
        );
      }
    });
  }

  resendCode() {
    this.countdown = 60;
    this.startCountdown();
    
    this.authService.sendVerificationCode(this.data.email).subscribe({
      next: () => {
        this.snackBar.open('New code sent successfully', 'Close', { duration: 3000 });
      },
      error: (error) => {
        this.snackBar.open(
          error.error?.message || 'Failed to resend code', 
          'Close', 
          { duration: 3000 }
        );
      }
    });
  }

  private startCountdown() {
    const interval = setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) clearInterval(interval);
    }, 1000);
  }
}