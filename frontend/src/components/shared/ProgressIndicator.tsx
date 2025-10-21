'use client';

import React from 'react';

interface ProgressStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

interface ProgressIndicatorProps {
  steps: ProgressStep[];
  correlationId?: string;
}

export default function ProgressIndicator({ steps, correlationId }: ProgressIndicatorProps) {
  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center space-x-4">
            {/* Step indicator */}
            <div className="flex-shrink-0">
              {step.status === 'completed' ? (
                <div className="w-8 h-8 bg-green-500 dark:bg-green-600 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              ) : step.status === 'active' ? (
                <div className="w-8 h-8 bg-blue-500 dark:bg-blue-600 rounded-full flex items-center justify-center animate-pulse">
                  <div className="w-3 h-3 bg-white rounded-full" />
                </div>
              ) : step.status === 'error' ? (
                <div className="w-8 h-8 bg-red-500 dark:bg-red-600 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
              ) : (
                <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                  <div className="w-3 h-3 bg-gray-400 dark:bg-gray-500 rounded-full" />
                </div>
              )}
            </div>

            {/* Step label */}
            <div className="flex-1">
              <p
                className={`text-sm font-medium ${
                  step.status === 'active'
                    ? 'text-blue-600 dark:text-blue-400'
                    : step.status === 'completed'
                    ? 'text-green-600 dark:text-green-400'
                    : step.status === 'error'
                    ? 'text-red-600 dark:text-red-400'
                    : 'text-gray-500 dark:text-gray-400'
                }`}
              >
                {step.label}
              </p>
            </div>

            {/* Loading spinner for active step */}
            {step.status === 'active' && (
              <div className="flex-shrink-0">
                <svg
                  className="animate-spin h-5 w-5 text-blue-500 dark:text-blue-400"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              </div>
            )}

            {/* Connecting line */}
            {index < steps.length - 1 && (
              <div className="absolute left-4 top-12 w-0.5 h-8 bg-gray-300 dark:bg-gray-600 ml-0.5" />
            )}
          </div>
        ))}
      </div>

      {/* Correlation ID for support */}
      {correlationId && (
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Request ID: <span className="font-mono">{correlationId}</span>
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            Save this ID if you need support assistance
          </p>
        </div>
      )}
    </div>
  );
}
