import { AbstractControl, ValidatorFn } from '@angular/forms';

export function emailValidator(): ValidatorFn {
  return (control: AbstractControl): { [key: string]: any } | null => {
    const value = control.value;
    if (!value) return null;
    
    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const valid = regex.test(value);
    return valid ? null : { invalidEmail: true };
  };
}