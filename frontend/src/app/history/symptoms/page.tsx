'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api-client';
import ProtectedRoute from '@/components/shared/ProtectedRoute';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { Calendar, AlertCircle, User, Clock, Activity } from 'lucide-react';
import Link from 'next/link';

interface SymptomRecord {
  id: number;
  symptoms: string;
  duration: string | null;
  age: number | null;
  sex: string | null;
  urgency_level: string;
  specialist_recommendation: string;
  reasoning: string | null;
  red_flags: string[];
  suggested_tests: string[];
  self_care_advice: string[];
  created_at: string;
}

export default function SymptomsHistoryPage() {
  return (
    <ProtectedRoute>
      <SymptomsHistoryContent />
    </ProtectedRoute>
  );
}

function SymptomsHistoryContent() {
  const { user, isLoading: authLoading } = useAuth();
  const [records, setRecords] = useState<SymptomRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Wait for auth to be ready
    if (authLoading) return;
    
    const fetchHistory = async () => {
      try {
        const response = await api.get<SymptomRecord[]>('/api/history/symptoms');
        setRecords(response.data);
      } catch (err: any) {
        setError('Failed to load symptom history');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, [authLoading]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <LoadingSpinner />
      </div>
    );
  }

  const getUrgencyColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'emergency':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'urgent':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'routine':
      case 'non-urgent':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Symptom History
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                View your past symptom analyses and recommendations
              </p>
            </div>
            <Link
              href="/symptoms"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              New Analysis
            </Link>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg">
            {error}
          </div>
        )}

        {/* Records List */}
        {records.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-12 text-center">
            <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No Symptom Records Yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Start by analyzing your symptoms to build your health history
            </p>
            <Link
              href="/symptoms"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Analyze Symptoms
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {records.map((record) => (
              <div
                key={record.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      {record.symptoms}
                    </h3>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {new Date(record.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </div>
                      {record.duration && (
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          Duration: {record.duration}
                        </div>
                      )}
                      {record.age && (
                        <div className="flex items-center gap-1">
                          <User className="w-4 h-4" />
                          Age: {record.age}
                        </div>
                      )}
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getUrgencyColor(record.urgency_level)}`}>
                    {record.urgency_level}
                  </span>
                </div>

                {/* Specialist Recommendation */}
                <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-1">
                    Recommended Specialist
                  </h4>
                  <p className="text-blue-800 dark:text-blue-300">
                    {record.specialist_recommendation}
                  </p>
                </div>

                {/* Reasoning */}
                {record.reasoning && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Analysis
                    </h4>
                    <p className="text-gray-700 dark:text-gray-300">
                      {record.reasoning}
                    </p>
                  </div>
                )}

                {/* Red Flags */}
                {record.red_flags && record.red_flags.length > 0 && (
                  <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-red-900 dark:text-red-200 mb-2">
                          Red Flags
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-red-800 dark:text-red-300">
                          {record.red_flags.map((flag, idx) => (
                            <li key={idx}>{flag}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* Suggested Tests */}
                {record.suggested_tests && record.suggested_tests.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Suggested Tests
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                      {record.suggested_tests.map((test, idx) => (
                        <li key={idx}>{test}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Self Care Advice */}
                {record.self_care_advice && record.self_care_advice.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Self-Care Advice
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                      {record.self_care_advice.map((advice, idx) => (
                        <li key={idx}>{advice}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
