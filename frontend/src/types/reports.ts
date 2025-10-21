/**
 * TypeScript type definitions for Medical Report Simplifier feature
 */

export interface KeyFinding {
  category: string;
  finding: string;
  original_term?: string;
  severity?: 'normal' | 'abnormal' | 'critical';
}

export interface ReportSimplifyRequest {
  text?: string;
  file_name?: string;
}

export interface ReportSimplifyResponse {
  summary: string;
  key_findings: KeyFinding[];
  recommended_specialist?: string;
  next_steps: string[];
  disclaimer: string;
  processed_at: string;
}
