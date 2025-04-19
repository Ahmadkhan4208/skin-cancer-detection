import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, take } from 'rxjs';
import { AuthService } from './services/auth.service';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatMenuModule,
    MatDividerModule
  ]
})
export class AppComponent {
  isAuthenticated$: Observable<boolean>;
  userEmail$: Observable<string | null>;
  userRole$: Observable<string | null>;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.isAuthenticated$ = this.authService.isAuthenticated;
    this.userEmail$ = this.authService.userEmail$;
    this.userRole$ = this.authService.userRole$;
  }

  getUsername(email: string | null): string {
    return email?.split('@')[0] || 'User';
  }

  openProfile(): void {
    this.authService.userRole$.pipe(take(1)).subscribe(role => {
      if (role === 'doctor') {
        this.router.navigate(['/doctor-profile']);
      } else if (role === 'patient') {
        this.router.navigate(['/patient-profile']);
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}