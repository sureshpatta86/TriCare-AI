'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api-client';
import ProtectedRoute from '@/components/shared/ProtectedRoute';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { Image as ImageIcon, Calendar, Activity } from 'lucide-react';
import Link from 'next/link';

interface ImagingRecord {
  id: number;
  file_name: string;
  file_type: string;
  body_part: string | null;
  prediction: string;
  confidence: number;
  findings: string | null;
  explanation: string | null;
  recommendations: string[];
  model_used: string | null;
  created_at: string;
}

export default function ImagingHistoryPage() {
  return (
    <ProtectedRoute>
      <ImagingHistoryContent />
    </ProtectedRoute>
  );
}

function ImagingHistoryContent() {
  const { user, isLoading: authLoading } = useAuth();
  const [records, setRecords] = useState<ImagingRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Wait for auth to be ready
    if (authLoading) return;
    
    const fetchHistory = async () => {
      try {
        const response = await api.get<ImagingRecord[]>('/api/history/imaging');
        setRecords(response.data);
      } catch (err: any) {
        setError('Failed to load imaging history');
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

  const getPredictionColor = (prediction: string) => {
    switch (prediction?.toLowerCase()) {
      case 'normal':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'abnormal':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 dark:text-green-400';
    if (confidence >= 0.6) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Imaging History
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                View your past medical imaging analyses
              </p>
            </div>
            <Link
              href="/imaging"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload New Image
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
            <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No Imaging Records Yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Upload a medical image to start building your history
            </p>
            <Link
              href="/imaging"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload Image
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
                      <ImageIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                        {record.file_name}
                      </h3>
                    </div>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {new Date(record.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </div>
                      {record.body_part && (
                        <div className="flex items-center gap-1">
                          <Activity className="w-4 h-4" />
                          {record.body_part}
                        </div>
                      )}
                      {record.model_used && (
                        <span className="text-xs text-gray-500 dark:text-gray-500">
                          Model: {record.model_used}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPredictionColor(record.prediction)}`}>
                    {record.prediction}
                  </span>
                </div>

                {/* Confidence */}
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Confidence
                    </span>
                    <span className={`text-sm font-semibold ${getConfidenceColor(record.confidence)}`}>
                      {(record.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        record.confidence >= 0.8
                          ? 'bg-green-600'
                          : record.confidence >= 0.6
                          ? 'bg-yellow-600'
                          : 'bg-red-600'
                      }`}
                      style={{ width: `${record.confidence * 100}%` }}
                    />
                  </div>
                </div>

                {/* Findings */}
                {record.findings && (
                  <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
                      Findings
                    </h4>
                    <p className="text-blue-800 dark:text-blue-300">
                      {record.findings}
                    </p>
                  </div>
                )}

                {/* Explanation */}
                {record.explanation && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Explanation
                    </h4>
                    <p className="text-gray-700 dark:text-gray-300">
                      {record.explanation}
                    </p>
                  </div>
                )}

                {/* Recommendations */}
                {record.recommendations && record.recommendations.length > 0 && (
                  <div>
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
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
