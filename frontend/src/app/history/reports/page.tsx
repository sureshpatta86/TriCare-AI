'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api-client';
import ProtectedRoute from '@/components/shared/ProtectedRoute';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { FileText, Calendar, AlertCircle } from 'lucide-react';
import Link from 'next/link';

interface ReportRecord {
  id: number;
  file_name: string | null;
  file_type: string | null;
  summary: string;
  key_findings: string[];
  recommendations: string[];
  specialist_needed: string | null;
  urgency_level: string | null;
  created_at: string;
}

export default function ReportsHistoryPage() {
  return (
    <ProtectedRoute>
      <ReportsHistoryContent />
    </ProtectedRoute>
  );
}

function ReportsHistoryContent() {
  const { user, isLoading: authLoading } = useAuth();
  const [records, setRecords] = useState<ReportRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Wait for auth to be ready
    if (authLoading) return;
    
    const fetchHistory = async () => {
      try {
        const response = await api.get<ReportRecord[]>('/api/history/reports');
        setRecords(response.data);
      } catch (err: any) {
        setError('Failed to load report history');
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

  const getUrgencyColor = (level: string | null) => {
    if (!level) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    
    switch (level.toLowerCase()) {
      case 'emergency':
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'urgent':
      case 'medium':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'routine':
      case 'low':
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
                Report History
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                View your past medical report analyses
              </p>
            </div>
            <Link
              href="/reports"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload New Report
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
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No Report Records Yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Upload a medical report to start building your history
            </p>
            <Link
              href="/reports"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload Report
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
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                        {record.file_name || 'Medical Report'}
                      </h3>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                      <Calendar className="w-4 h-4" />
                      {new Date(record.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </div>
                  </div>
                  {record.urgency_level && (
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getUrgencyColor(record.urgency_level)}`}>
                      {record.urgency_level}
                    </span>
                  )}
                </div>

                {/* Summary */}
                <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
                    Summary
                  </h4>
                  <p className="text-blue-800 dark:text-blue-300 whitespace-pre-wrap">
                    {record.summary}
                  </p>
                </div>

                {/* Key Findings */}
                {record.key_findings && record.key_findings.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Key Findings
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                      {record.key_findings.map((finding, idx) => (
                        <li key={idx}>{finding}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {record.recommendations && record.recommendations.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Recommendations
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                      {record.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Specialist Needed */}
                {record.specialist_needed && (
                  <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-purple-900 dark:text-purple-200 mb-1">
                          Specialist Consultation Recommended
                        </h4>
                        <p className="text-purple-800 dark:text-purple-300">
                          {record.specialist_needed}
                        </p>
                      </div>
                    </div>
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
