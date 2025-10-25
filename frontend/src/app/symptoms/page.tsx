'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Stethoscope, Send, Loader2, AlertCircle, UserCircle, Search } from 'lucide-react';
import { symptomFormSchema, type SymptomFormData } from '@/lib/validations/schemas';
import { routeSymptoms } from '@/lib/api-client';
import ProgressIndicator from '@/components/shared/ProgressIndicator';
import { useAuth } from '@/contexts/AuthContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8011';

interface RoutingResult {
  recommended_specialist: string;
  urgency_level: string;
  reasoning: string;
  red_flags?: string[];
  suggested_preparations?: string[];
  suggested_tests?: string[];
  home_care_tips?: string[];
}

interface ProgressStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

export default function SymptomsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RoutingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [correlationId, setCorrelationId] = useState<string | null>(null);
  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([
    { id: '1', label: 'Analyzing symptoms', status: 'pending' },
    { id: '2', label: 'Assessing urgency', status: 'pending' },
    { id: '3', label: 'Routing to specialist', status: 'pending' },
    { id: '4', label: 'Generating recommendations', status: 'pending' },
  ]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue
  } = useForm<SymptomFormData>({
    resolver: zodResolver(symptomFormSchema),
    mode: 'onBlur'
  });

  // Auto-populate age and sex from user profile
  useEffect(() => {
    if (user) {
      if (user.age) {
        setValue('age', user.age);
      }
      if (user.sex) {
        // Map sex values from profile to form values
        const genderMap: Record<string, 'male' | 'female' | 'other'> = {
          'Male': 'male',
          'Female': 'female',
          'Other': 'other'
        };
        const mappedGender = genderMap[user.sex];
        if (mappedGender) {
          setValue('gender', mappedGender);
        }
      }
    }
  }, [user, setValue]);

  const onSubmit = async (data: SymptomFormData) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setCorrelationId(null);

    try {
      // Step 1: Analyzing symptoms
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 0 ? { ...step, status: 'active' } : step
      ));
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Step 2: Assessing urgency
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 0 ? { ...step, status: 'completed' } : 
        idx === 1 ? { ...step, status: 'active' } : step
      ));
      
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Step 3: Routing to specialist
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 1 ? { ...step, status: 'completed' } : 
        idx === 2 ? { ...step, status: 'active' } : step
      ));

      const response = await routeSymptoms({
        symptoms: data.symptoms.trim(),
        age: data.age || undefined,
        sex: data.gender || undefined,
        duration: undefined,
        existing_conditions: undefined,
        current_medications: undefined
      });
      
      // Step 4: Generating recommendations
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 2 ? { ...step, status: 'completed' } : 
        idx === 3 ? { ...step, status: 'active' } : step
      ));
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Complete
      setProgressSteps(prev => prev.map(step => ({ ...step, status: 'completed' })));
      setResult(response);
      
    } catch (err: unknown) {
      const axiosError = err as { 
        response?: { 
          data?: { detail?: string; correlation_id?: string }; 
          headers?: Record<string, string>;
          status?: number;
        } 
      };
      
      // Extract correlation ID
      const corrId = axiosError.response?.headers?.['x-correlation-id'] || 
                     axiosError.response?.data?.correlation_id;
      if (corrId) {
        setCorrelationId(corrId);
      }
      
      // Mark current step as error
      setProgressSteps(prev => prev.map(step => 
        step.status === 'active' ? { ...step, status: 'error' } : step
      ));
      
      // Enhanced error messages
      if (axiosError.response?.status === 429) {
        setError('Too many requests. Please wait a moment and try again.');
      } else {
        setError(axiosError.response?.data?.detail || 'Failed to analyze symptoms. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency.toLowerCase()) {
      case 'emergency':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'urgent':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'routine':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full mb-4">
              <Stethoscope className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Symptom Router
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Describe your symptoms and get AI-powered specialist recommendations
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
            <div className="space-y-6">
              {/* Symptoms */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                  Symptoms *
                </label>
                <textarea
                  {...register('symptoms')}
                  placeholder="Describe your symptoms in detail (e.g., headache, fever, cough...)"
                  rows={5}
                  className={`w-full px-4 py-3 border rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none ${
                    errors.symptoms ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                  }`}
                />
                {errors.symptoms && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.symptoms.message}</p>
                )}
              </div>

              {/* Optional Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                    Age (optional)
                  </label>
                  <input
                    type="number"
                    {...register('age')}
                    placeholder="Your age"
                    min="0"
                    max="120"
                    className={`w-full px-4 py-3 border rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                      errors.age ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                    }`}
                  />
                  {errors.age && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.age.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                    Gender (optional)
                  </label>
                  <select
                    {...register('gender')}
                    className={`w-full px-4 py-3 border rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                      errors.gender ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                    }`}
                  >
                    <option value="">Select...</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                  {errors.gender && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.gender.message}</p>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white font-semibold py-4 px-6 rounded-xl transition-colors flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5 mr-2" />
                    Get Recommendation
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Error */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-8">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-3 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold text-red-900 dark:text-red-300 mb-1">Error</h3>
                  <p className="text-red-700 dark:text-red-400 mb-2">{error}</p>
                  {correlationId && (
                    <div className="mt-3 pt-3 border-t border-red-200 dark:border-red-800">
                      <p className="text-xs text-red-600 dark:text-red-400 font-mono">
                        Request ID: {correlationId}
                      </p>
                      <p className="text-xs text-red-500 dark:text-red-500 mt-1">
                        Please save this ID if you need support assistance
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Loading Progress */}
          {loading && (
            <div className="mb-8">
              <ProgressIndicator steps={progressSteps} correlationId={correlationId || undefined} />
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Recommendation
                </h2>
                <span className={`px-4 py-2 rounded-full text-sm font-semibold border ${getUrgencyColor(result.urgency_level)}`}>
                  {result.urgency_level.toUpperCase()}
                </span>
              </div>

              <div className="space-y-6">
                {/* Specialist */}
                <div className="bg-gradient-to-r from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 rounded-lg p-6">
                  <div className="flex items-start">
                    <UserCircle className="w-12 h-12 text-green-600 dark:text-green-400 mr-4 flex-shrink-0" />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        Recommended Specialist
                      </h3>
                      <p className="text-2xl font-bold text-green-700 dark:text-green-400 mb-4">
                        {result.recommended_specialist}
                      </p>
                      <button
                        onClick={() => {
                          // Extract just the specialist name (before any brackets, dashes, or special characters)
                          const specialistMatch = result.recommended_specialist.match(/^([A-Za-z\s]+?)(?:\s*\[|—|–|-{2,}|$)/);
                          let specialistName = specialistMatch ? specialistMatch[1].trim() : result.recommended_specialist.split(/[\[\—–-]/)[0].trim();
                          
                          // Map AI variations to our dropdown values
                          const specialistMapping: { [key: string]: string } = {
                            // Emergency & Urgent Care
                            'Emergency Department': 'Emergency Medicine',
                            'Emergency Room': 'Emergency Medicine',
                            'ER': 'Emergency Medicine',
                            'Urgent Care Clinic': 'Urgent Care',
                            'Urgent Care Center': 'Urgent Care',
                            
                            // Primary Care / Family Medicine
                            'Primary Care': 'Family Medicine',
                            'Primary Care Physician': 'Family Medicine',
                            'PCP': 'Family Medicine',
                            'Family Doctor': 'Family Medicine',
                            'General Practitioner': 'General Physician',
                            'GP': 'General Physician',
                            
                            // Cardiology
                            'Cardiac Specialist': 'Cardiologist',
                            'Heart Specialist': 'Cardiologist',
                            'Heart Doctor': 'Cardiologist',
                            
                            // Orthopedics
                            'Orthopedic Surgeon': 'Orthopedic',
                            'Orthopaedic': 'Orthopedic',
                            'Orthopaedic Surgeon': 'Orthopedic',
                            'Bone Specialist': 'Orthopedic',
                            
                            // ENT
                            'ENT': 'ENT Specialist',
                            'Ear Nose Throat': 'ENT Specialist',
                            'Otolaryngologist': 'ENT Specialist',
                            
                            // Mental Health
                            'Mental Health Specialist': 'Psychiatrist',
                            'Therapist': 'Psychologist',
                            'Counselor': 'Psychologist',
                            
                            // Neurology
                            'Brain Specialist': 'Neurologist',
                            'Nerve Specialist': 'Neurologist',
                            
                            // Gastroenterology
                            'GI Specialist': 'Gastroenterologist',
                            'Digestive Specialist': 'Gastroenterologist',
                            'Stomach Specialist': 'Gastroenterologist',
                            
                            // Pulmonology
                            'Lung Specialist': 'Pulmonologist',
                            'Respiratory Specialist': 'Pulmonologist',
                            
                            // Nephrology
                            'Kidney Specialist': 'Nephrologist',
                            'Renal Specialist': 'Nephrologist',
                            
                            // Endocrinology
                            'Diabetes Specialist': 'Endocrinologist',
                            'Hormone Specialist': 'Endocrinologist',
                            
                            // Dermatology
                            'Skin Specialist': 'Dermatologist',
                            'Skin Doctor': 'Dermatologist',
                            
                            // Ophthalmology
                            'Eye Specialist': 'Ophthalmologist',
                            'Eye Doctor': 'Ophthalmologist',
                            
                            // Oncology
                            'Cancer Specialist': 'Oncologist',
                            
                            // Urology
                            'Urinary Specialist': 'Urologist',
                            
                            // Gynecology
                            'OB/GYN': 'Gynecologist',
                            'OBGYN': 'Gynecologist',
                            'Women\'s Health': 'Gynecologist',
                            
                            // Pediatrics
                            'Child Specialist': 'Pediatrician',
                            'Children\'s Doctor': 'Pediatrician',
                            'Pediatric': 'Pediatrician',
                            
                            // Rheumatology
                            'Arthritis Specialist': 'Rheumatologist',
                            'Joint Specialist': 'Rheumatologist',
                            
                            // Surgery
                            'General Surgeon': 'Surgeon',
                            
                            // Podiatry
                            'Foot Specialist': 'Podiatrist',
                            'Foot Doctor': 'Podiatrist'
                          };
                          
                          // Check if we need to map the specialist name
                          specialistName = specialistMapping[specialistName] || specialistName;
                          
                          // Navigate to doctor finder with pre-selected specialization
                          router.push(`/doctors?specialization=${encodeURIComponent(specialistName)}`);
                        }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 
                                 text-white rounded-lg transition-colors font-medium"
                      >
                        <Search className="w-4 h-4" />
                        Find {result.recommended_specialist.match(/^([A-Za-z\s]+?)(?:\s*\[|—|–|-{2,}|$)/)?.[1]?.trim() || result.recommended_specialist.split(/[\[\—–-]/)[0].trim()}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Red Flags */}
                {result.red_flags && result.red_flags.length > 0 && (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-red-900 dark:text-red-300 mb-3 flex items-center">
                      <AlertCircle className="w-5 h-5 mr-2" />
                      Warning Signs to Watch For
                    </h3>
                    <ul className="space-y-2">
                      {result.red_flags.map((flag: string, index: number) => (
                        <li key={index} className="flex items-start text-red-800 dark:text-red-300">
                          <span className="inline-block w-2 h-2 bg-red-600 dark:bg-red-400 rounded-full mr-3 mt-2 flex-shrink-0" />
                          <span>{flag}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Reasoning */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                    Analysis
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {result.reasoning}
                    </p>
                  </div>
                </div>

                {/* Suggested Preparations */}
                {result.suggested_preparations && result.suggested_preparations.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      What to Prepare
                    </h3>
                    <ul className="space-y-2">
                      {result.suggested_preparations.map((prep: string, index: number) => (
                        <li key={index} className="flex items-start">
                          <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-600 dark:bg-blue-500 text-white rounded-full mr-3 flex-shrink-0 text-sm font-semibold">
                            {index + 1}
                          </span>
                          <span className="text-gray-700 dark:text-gray-300 pt-0.5">{prep}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Suggested Tests */}
                {result.suggested_tests && result.suggested_tests.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      Tests That May Be Ordered
                    </h3>
                    <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                      <ul className="space-y-2">
                        {result.suggested_tests.map((test: string, index: number) => (
                          <li key={index} className="flex items-start text-gray-700 dark:text-gray-300">
                            <span className="inline-block w-2 h-2 bg-purple-600 dark:bg-purple-400 rounded-full mr-3 mt-2 flex-shrink-0" />
                            <span>{test}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Home Care Tips */}
                {result.home_care_tips && result.home_care_tips.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      Home Care Tips
                    </h3>
                    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                      <ul className="space-y-2">
                        {result.home_care_tips.map((tip: string, index: number) => (
                          <li key={index} className="flex items-start text-gray-700 dark:text-gray-300">
                            <span className="inline-block w-2 h-2 bg-green-600 dark:bg-green-400 rounded-full mr-3 mt-2 flex-shrink-0" />
                            <span>{tip}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                  ⚠️ This is an AI-generated recommendation. Always consult with a qualified healthcare provider for proper diagnosis and treatment.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
