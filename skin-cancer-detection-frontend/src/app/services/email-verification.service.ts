import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class EmailVerificationService {
  private blockedDomains = ['tempmail.com', 'mailinator.com']; // Add more as needed

  constructor(private http: HttpClient) {}

  /**
   * Comprehensive email verification
   * @param email 
   * @returns Observable<boolean> indicating if email is valid
   */
  verify(email: string): Observable<boolean> {
    // Step 1: Basic format validation
    if (!this.isValidFormat(email)) {
      return of(false);
    }

    // Step 2: Check against blocked domains
    if (this.isBlockedDomain(email)) {
      return of(false);
    }
    return of(true);
  }

  /**
   * Basic email format validation
   */
  private isValidFormat(email: string): boolean {
    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return regex.test(email);
  }

  /**
   * Checks against known disposable email domains
   */
  private isBlockedDomain(email: string): boolean {
    const domain = email.split('@')[1]?.toLowerCase();
    return domain ? this.blockedDomains.includes(domain) : true;
  }

}