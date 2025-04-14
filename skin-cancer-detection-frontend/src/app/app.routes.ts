import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { ImageUploadComponent } from './components/image-upload/image-upload.component';
import { LoginComponent } from './components/auth/login/login.component';
import { RegisterComponent } from './components/auth/register/register.component';

export const routes: Routes = [
  { 
    path: '', 
    redirectTo: 'analyze', 
    pathMatch: 'full' 
  },
  { 
    path: 'analyze', 
    component: ImageUploadComponent,
    canActivate: [AuthGuard] 
  },
  { 
    path: 'login', 
    component: LoginComponent 
  },
  { 
    path: 'register', 
    component: RegisterComponent 
  },
  { 
    path: '**', 
    redirectTo: 'login' 
  }
];