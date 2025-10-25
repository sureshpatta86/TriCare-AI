'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/shared/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api-client';
import { FileText, Stethoscope, Image as ImageIcon, Users, Activity, Calendar, TrendingUp } from 'lucide-react';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import Link from 'next/link';

interface DashboardStats {
  total_reports: number;
  total_symptoms: number;
  total_imaging: number;
  favorite_doctors_count: number;
  recent_reports: any[];
  recent_symptoms: any[];
  recent_imaging: any[];
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const { user, isLoading: authLoading } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Wait for auth to be ready before fetching
    if (authLoading) return;
    
    const fetchDashboardData = async () => {
      try {
        const response = await api.get<DashboardStats>('/api/history/dashboard');
        setStats(response.data);
      } catch (err: any) {
        setError('Failed to load dashboard data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [authLoading]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="container mx-auto px-4">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back, {user?.full_name || user?.username}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Here's an overview of your health journey
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Medical Reports"
            value={stats?.total_reports || 0}
            icon={FileText}
            color="blue"
            link="/history/reports"
          />
          <StatCard
            title="Symptom Checks"
            value={stats?.total_symptoms || 0}
            icon={Stethoscope}
            color="purple"
            link="/history/symptoms"
          />
          <StatCard
            title="Imaging Scans"
            value={stats?.total_imaging || 0}
            icon={ImageIcon}
            color="green"
            link="/history/imaging"
          />
          <StatCard
            title="Favorite Doctors"
            value={stats?.favorite_doctors_count || 0}
            icon={Users}
            color="orange"
            link="/favorites"
          />
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Reports */}
          <RecentActivityCard
            title="Recent Medical Reports"
            items={stats?.recent_reports || []}
            icon={FileText}
            emptyMessage="No reports yet"
            viewAllLink="/history/reports"
          />

          {/* Recent Symptoms */}
          <RecentActivityCard
            title="Recent Symptom Checks"
            items={stats?.recent_symptoms || []}
            icon={Stethoscope}
            emptyMessage="No symptom checks yet"
            viewAllLink="/history/symptoms"
          />
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/reports"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-medical-500 dark:hover:border-medical-500 transition-colors"
            >
              <FileText className="w-6 h-6 text-medical-600 dark:text-medical-400" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Analyze Report</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Upload medical document</p>
              </div>
            </Link>

            <Link
              href="/symptoms"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-medical-500 dark:hover:border-medical-500 transition-colors"
            >
              <Stethoscope className="w-6 h-6 text-medical-600 dark:text-medical-400" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Check Symptoms</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Get specialist guidance</p>
              </div>
            </Link>

            <Link
              href="/doctors"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-medical-500 dark:hover:border-medical-500 transition-colors"
            >
              <Users className="w-6 h-6 text-medical-600 dark:text-medical-400" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Find Doctors</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Search by location</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: number;
  icon: any;
  color: 'blue' | 'purple' | 'green' | 'orange';
  link: string;
}

function StatCard({ title, value, icon: Icon, color, link }: StatCardProps) {
  const colorClasses = {
    blue: 'from-blue-500 to-cyan-500',
    purple: 'from-purple-500 to-pink-500',
    green: 'from-green-500 to-emerald-500',
    orange: 'from-orange-500 to-red-500',
  };

  return (
    <Link href={link}>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{title}</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
          </div>
          <div className={`p-3 rounded-lg bg-gradient-to-br ${colorClasses[color]}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>
      </div>
    </Link>
  );
}

interface RecentActivityCardProps {
  title: string;
  items: any[];
  icon: any;
  emptyMessage: string;
  viewAllLink: string;
}

function RecentActivityCard({ title, items, icon: Icon, emptyMessage, viewAllLink }: RecentActivityCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Icon className="w-5 h-5" />
          {title}
        </h2>
      </div>
      <div className="p-6">
        {items.length === 0 ? (
          <p className="text-center text-gray-500 dark:text-gray-400 py-8">{emptyMessage}</p>
        ) : (
          <div className="space-y-4">
            {items.slice(0, 3).map((item, index) => (
              <div key={index} className="flex items-start gap-3 pb-4 border-b border-gray-100 dark:border-gray-700 last:border-0">
                <Calendar className="w-5 h-5 text-gray-400 mt-1" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">
                    {item.summary || item.symptoms || item.findings || 'No title'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
        <Link
          href={viewAllLink}
          className="mt-4 block text-center text-sm text-medical-600 dark:text-medical-400 hover:text-medical-700 dark:hover:text-medical-300 font-medium"
        >
          View all →
        </Link>
      </div>
    </div>
  );
}
