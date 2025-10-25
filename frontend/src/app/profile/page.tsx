'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/shared/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { User, Mail, Phone, Calendar, Droplet, AlertCircle, Pill, Heart, Save, Check, MapPin } from 'lucide-react';
import LoadingSpinner from '@/components/shared/LoadingSpinner';

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
}

function ProfileContent() {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    age: user?.age || '',
    sex: user?.sex || '',
    phone: user?.phone || '',
    postal_code: user?.postal_code || '',
    blood_type: user?.blood_type || '',
    allergies: user?.allergies || '',
    chronic_conditions: user?.chronic_conditions || '',
    current_medications: user?.current_medications || '',
    emergency_contact: user?.emergency_contact || '',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        age: user.age?.toString() || '',
        sex: user.sex || '',
        phone: user.phone || '',
        postal_code: user.postal_code || '',
        blood_type: user.blood_type || '',
        allergies: user.allergies || '',
        chronic_conditions: user.chronic_conditions || '',
        current_medications: user.current_medications || '',
        emergency_contact: user.emergency_contact || '',
      });
    }
  }, [user]);

  const handleSave = async () => {
    setError('');
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      await updateProfile({
        ...formData,
        age: formData.age ? parseInt(formData.age.toString()) : undefined,
      });
      setIsEditing(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Profile Settings
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Manage your personal and medical information
            </p>
          </div>
          
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="px-6 py-2 bg-medical-600 dark:bg-medical-500 hover:bg-medical-700 dark:hover:bg-medical-600 
                       text-white rounded-lg transition-colors font-medium"
            >
              Edit Profile
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setIsEditing(false);
                  setError('');
                  // Reset form data
                  if (user) {
                    setFormData({
                      full_name: user.full_name || '',
                      age: user.age?.toString() || '',
                      sex: user.sex || '',
                      phone: user.phone || '',
                      postal_code: user.postal_code || '',
                      blood_type: user.blood_type || '',
                      allergies: user.allergies || '',
                      chronic_conditions: user.chronic_conditions || '',
                      current_medications: user.current_medications || '',
                      emergency_contact: user.emergency_contact || '',
                    });
                  }
                }}
                className="px-6 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 
                         text-gray-900 dark:text-white rounded-lg transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-6 py-2 bg-medical-600 dark:bg-medical-500 hover:bg-medical-700 dark:hover:bg-medical-600 
                         disabled:bg-gray-400 text-white rounded-lg transition-colors font-medium flex items-center gap-2"
              >
                {isSaving ? (
                  <>
                    <LoadingSpinner size="sm" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Success Message */}
        {saveSuccess && (
          <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-center gap-3">
            <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
            <p className="text-green-600 dark:text-green-400 font-medium">Profile updated successfully!</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Account Information */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 mb-6">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <User className="w-5 h-5" />
              Account Information
            </h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email
                </label>
                <div className="flex items-center gap-2 px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-900 dark:text-white">{user?.email}</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Username
                </label>
                <div className="flex items-center gap-2 px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                  <User className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-900 dark:text-white">{user?.username}</span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Full Name
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                           focus:ring-2 focus:ring-medical-500 focus:border-transparent
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Your full name"
                />
              ) : (
                <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                  <span className="text-gray-900 dark:text-white">{user?.full_name || 'Not set'}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Personal Information */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 mb-6">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Personal Information
            </h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Age
                </label>
                {isEditing ? (
                  <input
                    type="number"
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                             focus:ring-2 focus:ring-medical-500 focus:border-transparent
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Age"
                    min="0"
                    max="150"
                  />
                ) : (
                  <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="text-gray-900 dark:text-white">{user?.age || 'Not set'}</span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Sex
                </label>
                {isEditing ? (
                  <select
                    value={formData.sex}
                    onChange={(e) => setFormData({ ...formData, sex: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                             focus:ring-2 focus:ring-medical-500 focus:border-transparent
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="">Select</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                ) : (
                  <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="text-gray-900 dark:text-white">{user?.sex || 'Not set'}</span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Blood Type
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={formData.blood_type}
                    onChange={(e) => setFormData({ ...formData, blood_type: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                             focus:ring-2 focus:ring-medical-500 focus:border-transparent
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="e.g., O+"
                  />
                ) : (
                  <div className="flex items-center gap-2 px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <Droplet className="w-4 h-4 text-red-500" />
                    <span className="text-gray-900 dark:text-white">{user?.blood_type || 'Not set'}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Phone className="inline w-4 h-4 mr-1" />
                  Phone Number
                </label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                             focus:ring-2 focus:ring-medical-500 focus:border-transparent
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Your phone number"
                  />
                ) : (
                  <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="text-gray-900 dark:text-white">{user?.phone || 'Not set'}</span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <MapPin className="inline w-4 h-4 mr-1" />
                  Postal Code
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={formData.postal_code}
                    onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                             focus:ring-2 focus:ring-medical-500 focus:border-transparent
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="e.g., 12345"
                  />
                ) : (
                  <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="text-gray-900 dark:text-white">{user?.postal_code || 'Not set'}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Medical Information */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <Heart className="w-5 h-5" />
              Medical Information
            </h2>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <AlertCircle className="inline w-4 h-4 mr-1" />
                Allergies
              </label>
              {isEditing ? (
                <textarea
                  value={formData.allergies}
                  onChange={(e) => setFormData({ ...formData, allergies: e.target.value })}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                           focus:ring-2 focus:ring-medical-500 focus:border-transparent
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="List any allergies (medications, food, environmental)"
                />
              ) : (
                <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 min-h-[60px]">
                  <span className="text-gray-900 dark:text-white">{user?.allergies || 'None listed'}</span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Heart className="inline w-4 h-4 mr-1" />
                Chronic Conditions
              </label>
              {isEditing ? (
                <textarea
                  value={formData.chronic_conditions}
                  onChange={(e) => setFormData({ ...formData, chronic_conditions: e.target.value })}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                           focus:ring-2 focus:ring-medical-500 focus:border-transparent
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="List any chronic conditions or diseases"
                />
              ) : (
                <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 min-h-[60px]">
                  <span className="text-gray-900 dark:text-white">{user?.chronic_conditions || 'None listed'}</span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Pill className="inline w-4 h-4 mr-1" />
                Current Medications
              </label>
              {isEditing ? (
                <textarea
                  value={formData.current_medications}
                  onChange={(e) => setFormData({ ...formData, current_medications: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                           focus:ring-2 focus:ring-medical-500 focus:border-transparent
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="List current medications with dosage"
                />
              ) : (
                <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 min-h-[80px]">
                  <span className="text-gray-900 dark:text-white">{user?.current_medications || 'None listed'}</span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Phone className="inline w-4 h-4 mr-1" />
                Emergency Contact
              </label>
              {isEditing ? (
                <textarea
                  value={formData.emergency_contact}
                  onChange={(e) => setFormData({ ...formData, emergency_contact: e.target.value })}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg 
                           focus:ring-2 focus:ring-medical-500 focus:border-transparent
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Name, relationship, phone number"
                />
              ) : (
                <div className="px-4 py-2.5 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 min-h-[60px]">
                  <span className="text-gray-900 dark:text-white">{user?.emergency_contact || 'Not set'}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
