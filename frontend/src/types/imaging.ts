/**
 * TypeScript type definitions for Imaging Pre-Screen feature
 */

export type PredictionClass = 'normal' | 'abnormal' | 'uncertain';

export interface ImagingPrescreenRequest {
  image_type: string;
  body_part?: string;
}

export interface ImagingPrescreenResponse {
  prediction: PredictionClass;
  confidence: number;
  explanation: string;
  areas_of_interest: string[];
  recommended_next_steps: string[];
  recommended_specialist?: string;
  heatmap_available: boolean;
  heatmap_base64?: string;
  model_used: string;
  fallback_used: boolean;
  disclaimer: string;
  processed_at: string;
}
