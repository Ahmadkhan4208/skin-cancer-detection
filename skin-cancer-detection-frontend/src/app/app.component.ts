import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { AuthService } from './services/auth.service';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RouterModule, RouterOutlet } from '@angular/router';

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
    MatTooltipModule
  ]
})
export class AppComponent {
  isAuthenticated$: Observable<boolean>;
  userEmail$: Observable<string | null>;
  userRole$: Observable<string | null>;

  constructor(private authService: AuthService) {
    this.isAuthenticated$ = this.authService.isAuthenticated();
    this.userEmail$ = this.authService.userEmail$;
    this.userRole$ = this.authService.userRole$;
  }

  logout(): void {
    this.authService.logout();
  }
  getUsername(email: string | null): string {
    return email?.split('@')[0] || '';
  }
}