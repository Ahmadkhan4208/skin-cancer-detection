import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { provideRouter } from '@angular/router';
import { routes } from './app/app.routes';

// Merge the existing appConfig with additional router provider
const mergedConfig = {
  ...appConfig,  // Preserve all existing configuration
  providers: [
    ...(appConfig.providers || []),  // Keep existing providers
    provideRouter(routes)             // Add router provider
  ]
};

bootstrapApplication(AppComponent, mergedConfig)
  .catch((err) => console.error(err));