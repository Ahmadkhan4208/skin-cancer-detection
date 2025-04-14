import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { isPlatformBrowser } from '@angular/common';

interface LoginResponse {
  access_token: string;
  token_type: string;
  email: string;  // Added email to the response interface
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  private userEmailSubject = new BehaviorSubject<string | null>(null); // Track user email
  private token: string | null = null;
  private isBrowser: boolean;
  private pendingRegistration: { email: string, password: string } | null = null;

  constructor(
    private http: HttpClient, 
    private router: Router,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
    this.initializeAuthState();
  }

  // Expose email as observable
  get userEmail$(): Observable<string | null> {
    return this.userEmailSubject.asObservable();
  }

  private initializeAuthState(): void {
    if (this.isBrowser) {
      this.token = localStorage.getItem('access_token');
      const email = localStorage.getItem('user_email');
      this.isAuthenticatedSubject.next(!!this.token);
      this.userEmailSubject.next(email);
    }
  }

  private setToken(token: string, email: string): void {
    this.token = token;
    if (this.isBrowser) {
      localStorage.setItem('access_token', token);
      localStorage.setItem('user_email', email);
    }
    this.isAuthenticatedSubject.next(true);
    this.userEmailSubject.next(email);
  }

  private removeToken(): void {
    this.token = null;
    if (this.isBrowser) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_email');
    }
    this.isAuthenticatedSubject.next(false);
    this.userEmailSubject.next(null);
  }

  login(email: string, password: string): Observable<LoginResponse> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    return this.http.post<LoginResponse>(`${this.apiUrl}/token`, formData).pipe(
      tap(response => {
        this.setToken(response.access_token, response.email);
      })
    );
  }

  /**
   * Step 1: Initiate registration by sending verification email
   */
  sendVerificationEmail(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/send-verification`, { email });
  }

  /**
   * Step 2: Verify the code received via email
   */
  verifyCode(email: string, code: string): Observable<{ verified: boolean }> {
    return this.http.post<{ verified: boolean }>(
      `${this.apiUrl}/verify-code`, 
      { email, code }
    );
  }

  /**
   * Step 3: Complete registration after verification
   */
  completeRegistration(email: string, password: string, role: string): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    return this.http.post(`${this.apiUrl}/register`, 
      { email: email, password: password },
      { headers: headers }
    ).pipe(
      tap((response: any) => {
        if (response.access_token) {
          this.setToken(response.access_token, email);
        }
      })
    );
  }

  /**
   * Store pending registration data (between verification steps)
   */
  storePendingRegistration(email: string, password: string): void {
    this.pendingRegistration = { email, password };
  }

  /**
   * Clear pending registration data
   */
  clearPendingRegistration(): void {
    this.pendingRegistration = null;
  }

  /**
   * Get pending registration data
   */
  getPendingRegistration(): { email: string, password: string } | null {
    return this.pendingRegistration;
  }

  logout(): void {
    this.removeToken();
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return this.token;
  }

  isAuthenticated(): Observable<boolean> {
    return this.isAuthenticatedSubject.asObservable();
  }

  getCurrentUserEmail(): string | null {
    return this.userEmailSubject.value;
  }
}