/**
 * TypeScript type definitions for Doctor Finder feature
 */

export interface DoctorSearchRequest {
  pincode: string;
  specialization?: string; // Optional - shows all doctors if not specified
  radius_km?: number;
  limit?: number; // Maximum number of results to return (default: 50)
}

export interface DoctorLocation {
  latitude: number;
  longitude: number;
  address: string;
  city: string;
  state: string;
  pincode: string;
}

export interface Doctor {
  id: string;
  name: string;
  specialization: string;
  qualification: string;
  experience_years: number;
  rating: number;
  location: DoctorLocation;
  distance_km: number;
  phone: string;
  email?: string;
  clinic_name: string;
  consultation_fee?: number;
  available_days: string[];
  available_hours: string;
  languages: string[];
}

export interface DoctorSearchResponse {
  user_location: {
    latitude: number;
    longitude: number;
    address: string;
    pincode?: string;
  };
  search_radius_km: number;
  specialization: string;
  total_doctors_found: number;
  doctors: Doctor[];
  processed_at: string;
}

export interface Specialization {
  label: string;
  value: string;
}

export interface FavoriteDoctorCreate {
  doctor_id: string;
  doctor_name: string;
  specialization: string;
  clinic_name?: string;
  phone?: string;
  address?: string;
  notes?: string;
}

export interface FavoriteDoctorUpdate {
  notes?: string;
  last_visit?: string;
  next_appointment?: string;
}

export interface FavoriteDoctor {
  id: number;
  user_id: number;
  doctor_id: string;
  doctor_name: string;
  specialization: string;
  clinic_name?: string;
  phone?: string;
  address?: string;
  notes?: string;
  last_visit?: string;
  next_appointment?: string;
  created_at: string;
}
