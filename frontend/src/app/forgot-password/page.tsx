'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Mail, ArrowLeft, Loader2, CheckCircle } from 'lucide-react';
import { api } from '@/lib/api-client';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [resetLink, setResetLink] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await api.post('/api/auth/forgot-password', { email });
      setSuccess(true);
      
      // In development, we get the reset link
      if (response.data.reset_link) {
        setResetLink(response.data.reset_link);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send reset link');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 w-full max-w-md">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Check Your Email
            </h1>
            
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              If an account exists for <strong>{email}</strong>, we've sent a password reset link.
            </p>

            {resetLink && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-900 dark:text-blue-300 mb-2 font-semibold">
                  Development Mode - Reset Link:
                </p>
                <Link 
                  href={resetLink.replace('http://localhost:3000', '')}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline break-all"
                >
                  {resetLink}
                </Link>
              </div>
            )}

            <div className="space-y-3">
              <Link
                href="/login"
                className="block w-full py-3 px-4 bg-medical-600 dark:bg-medical-500 hover:bg-medical-700 
                         dark:hover:bg-medical-600 text-white rounded-lg font-medium transition-colors"
              >
                Back to Login
              </Link>
              
              <button
                onClick={() => {
                  setSuccess(false);
                  setEmail('');
                  setResetLink('');
                }}
                className="block w-full py-3 px-4 border border-gray-300 dark:border-gray-600 
                         hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 
                         rounded-lg font-medium transition-colors"
              >
                Send Another Link
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-medical-100 dark:bg-medical-900/30 rounded-full flex items-center justify-center mb-4">
            <Mail className="w-8 h-8 text-medical-600 dark:text-medical-400" />
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Forgot Password?
          </h1>
          
          <p className="text-gray-600 dark:text-gray-400">
            Enter your email and we'll send you a link to reset your password
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg 
                       focus:ring-2 focus:ring-medical-500 focus:border-transparent
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       placeholder-gray-400 dark:placeholder-gray-500"
              placeholder="your@email.com"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-medical-600 dark:bg-medical-500 hover:bg-medical-700 
                     dark:hover:bg-medical-600 disabled:bg-gray-400 dark:disabled:bg-gray-600 
                     text-white font-semibold py-3 px-6 rounded-lg transition-colors 
                     flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Mail className="w-5 h-5 mr-2" />
                Send Reset Link
              </>
            )}
          </button>
        </form>

        {/* Back to Login */}
        <div className="mt-6 text-center">
          <Link
            href="/login"
            className="inline-flex items-center text-medical-600 dark:text-medical-400 
                     hover:text-medical-700 dark:hover:text-medical-300 font-medium"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
}
