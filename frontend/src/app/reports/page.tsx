'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useDropzone } from 'react-dropzone';
import { FileText, Upload, Loader2, AlertCircle, Search } from 'lucide-react';
import { reportFileSchema, type ReportFileData } from '@/lib/validations/schemas';
import { simplifyReport } from '@/lib/api-client';
import ProgressIndicator from '@/components/shared/ProgressIndicator';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8011';

interface KeyFinding {
  category: string;
  finding: string;
  original_term?: string;
  severity?: string;
}

interface ReportResult {
  summary?: string;
  key_findings?: KeyFinding[];
  recommended_specialist?: string;
  next_steps?: string[];
}

interface ProgressStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

export default function ReportsPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [correlationId, setCorrelationId] = useState<string | null>(null);
  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([
    { id: '1', label: 'Uploading document', status: 'pending' },
    { id: '2', label: 'Extracting text', status: 'pending' },
    { id: '3', label: 'Analyzing content', status: 'pending' },
    { id: '4', label: 'Generating summary', status: 'pending' },
  ]);

  const {
    setValue,
    handleSubmit,
    formState: { errors },
    clearErrors
  } = useForm<ReportFileData>({
    resolver: zodResolver(reportFileSchema)
  });

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const selectedFile = acceptedFiles[0];
        setFile(selectedFile);
        setValue('file', selectedFile);
        clearErrors('file');
        setError(null);
        setResult(null);
      }
    }
  });

  const onSubmit = async (data: ReportFileData) => {
    if (!data.file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setCorrelationId(null);

    const formData = new FormData();
    formData.append('file', data.file);

    try {
      // Step 1: Uploading
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 0 ? { ...step, status: 'active' } : step
      ));
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Step 2: Extracting text
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 0 ? { ...step, status: 'completed' } : 
        idx === 1 ? { ...step, status: 'active' } : step
      ));
      
      await new Promise(resolve => setTimeout(resolve, 400));
      
      // Step 3: Analyzing
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 1 ? { ...step, status: 'completed' } : 
        idx === 2 ? { ...step, status: 'active' } : step
      ));

      const response = await simplifyReport(data.file);
      
      // Step 4: Generating summary
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
      if (axiosError.response?.status === 413) {
        setError('File is too large. Maximum size is 5MB.');
      } else if (axiosError.response?.status === 415) {
        setError('Unsupported file type. Please upload PDF, TXT, DOC, DOCX, or image files.');
      } else if (axiosError.response?.status === 429) {
        setError('Too many requests. Please wait a moment and try again.');
      } else {
        setError(axiosError.response?.data?.detail || 'Failed to process report. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
              <FileText className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Medical Report Simplifier
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Upload your medical report (PDF or image) and get an easy-to-understand summary
            </p>
          </div>

          {/* Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
            <form onSubmit={handleSubmit(onSubmit)}>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
                  isDragActive
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : errors.file
                    ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                {file ? (
                  <div>
                    <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      {file.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-2">
                      Drop your medical report here, or click to browse
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Supports PDF, PNG, JPG (Max 10MB)
                    </p>
                  </div>
                )}
              </div>
              {errors.file && (
                <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.file.message as string}</p>
              )}

              {file && (
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full mt-6 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white font-semibold py-4 px-6 rounded-xl transition-colors flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    'Simplify Report'
                  )}
                </button>
              )}
            </form>
          </div>

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
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Simplified Summary
              </h2>
              
              <div className="space-y-6">
                {result.summary && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      Summary
                    </h3>
                    <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
                      <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                        {result.summary}
                      </p>
                    </div>
                  </div>
                )}

                {result.key_findings && result.key_findings.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      Key Findings
                    </h3>
                    <div className="space-y-4">
                      {result.key_findings.map((finding, index) => (
                        <div key={index} className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 border-l-4 border-blue-500">
                          <div className="flex items-start justify-between mb-2">
                            <span className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wide">
                              {finding.category}
                            </span>
                            {finding.severity && (
                              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                                finding.severity === 'critical' 
                                  ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                                  : finding.severity === 'abnormal'
                                  ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
                                  : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                              }`}>
                                {finding.severity}
                              </span>
                            )}
                          </div>
                          <p className="text-gray-700 dark:text-gray-300 mb-2">
                            {finding.finding}
                          </p>
                          {finding.original_term && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                              Medical term: {finding.original_term}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.recommended_specialist && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      Recommended Specialist
                    </h3>
                    <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                      <p className="text-gray-700 dark:text-gray-300 mb-3">
                        {result.recommended_specialist}
                      </p>
                      <button
                        onClick={() => {
                          if (result.recommended_specialist) {
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
                            
                            router.push(`/doctors?specialization=${encodeURIComponent(specialistName)}`);
                          }
                        }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 
                                 text-white rounded-lg transition-colors font-medium"
                      >
                        <Search className="w-4 h-4" />
                        Find {result.recommended_specialist.match(/^([A-Za-z\s]+?)(?:\s*\[|—|–|-{2,}|$)/)?.[1]?.trim() || result.recommended_specialist.split(/[\[\—–-]/)[0].trim()}
                      </button>
                    </div>
                  </div>
                )}

                {result.next_steps && result.next_steps.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      Next Steps
                    </h3>
                    <ul className="space-y-2">
                      {result.next_steps.map((step, index) => (
                        <li key={index} className="flex items-start">
                          <span className="inline-flex items-center justify-center w-6 h-6 bg-green-600 dark:bg-green-500 text-white text-sm font-semibold rounded-full mr-3 flex-shrink-0">
                            {index + 1}
                          </span>
                          <span className="text-gray-700 dark:text-gray-300 pt-0.5">{step}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                  ⚠️ This is an AI-generated summary. Always consult with your healthcare provider for medical advice.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
