/**
 * TypeScript type definitions for Symptom Router feature
 */

export type UrgencyLevel = 'emergency' | 'urgent' | 'routine' | 'non-urgent';

export interface SymptomRouteRequest {
  symptoms: string;
  age?: number;
  sex?: string;
  duration?: string;
  existing_conditions?: string[];
  current_medications?: string[];
}

export interface SymptomRouteResponse {
  recommended_specialist: string;
  urgency_level: UrgencyLevel;
  reasoning: string;
  red_flags: string[];
  suggested_preparations: string[];
  suggested_tests: string[];
  home_care_tips: string[];
  disclaimer: string;
  processed_at: string;
}
