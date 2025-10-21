/**
 * Disclaimer Banner Component
 * 
 * Prominent medical disclaimer banner for all features
 */

'use client';

import { AlertTriangle } from 'lucide-react';

interface DisclaimerBannerProps {
  type?: 'general' | 'reports' | 'symptoms' | 'imaging';
}

const DISCLAIMERS = {
  general: 'This is an educational tool only. Not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.',
  reports: 'This report simplification is for educational purposes only. It is NOT a medical interpretation. Always have your reports reviewed by a licensed healthcare professional.',
  symptoms: 'This symptom guidance is educational only. If you experience severe symptoms or emergency signs, seek immediate medical attention. Call 911 for emergencies.',
  imaging: 'This is NOT a diagnostic tool. All medical imaging MUST be reviewed by a qualified radiologist. Do not make medical decisions based on this AI analysis.',
};

export default function DisclaimerBanner({ type = 'general' }: DisclaimerBannerProps) {
  const message = DISCLAIMERS[type];

  return (
    <div className="rounded-lg border-2 border-urgent-300 bg-urgent-50 p-4">
      <div className="flex items-start space-x-3">
        <AlertTriangle className="h-5 w-5 text-urgent-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-urgent-900 mb-1">
            Important Medical Disclaimer
          </h3>
          <p className="text-sm text-urgent-800 leading-relaxed">
            {message}
          </p>
        </div>
      </div>
    </div>
  );
}
