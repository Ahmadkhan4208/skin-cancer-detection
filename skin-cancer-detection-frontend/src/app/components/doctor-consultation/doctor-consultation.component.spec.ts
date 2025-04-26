import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DoctorConsultationComponent } from './doctor-consultation.component';

describe('DoctorConsultationComponent', () => {
  let component: DoctorConsultationComponent;
  let fixture: ComponentFixture<DoctorConsultationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DoctorConsultationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DoctorConsultationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
