'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import { Search, MapPin, Phone, Mail, Clock, Star, Navigation, Filter, Heart } from 'lucide-react';
import { DoctorSearchRequest, DoctorSearchResponse, Doctor } from '@/types/doctors';
import { api, addFavoriteDoctor, removeFavoriteDoctor, getFavoriteDoctors } from '@/lib/api-client';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { useAuth } from '@/contexts/AuthContext';

// Dynamically import the map component (client-side only)
const DoctorMap = dynamic(() => import('@/components/doctors/DoctorMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-96 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
      <LoadingSpinner />
    </div>
  ),
});

function DoctorFinderContent() {
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const [pincode, setPincode] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [limit, setLimit] = useState(50);
  const [searchResults, setSearchResults] = useState<DoctorSearchResponse | null>(null);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [correlationId, setCorrelationId] = useState('');
  const [progress, setProgress] = useState(0);
  const [favoriteDoctorIds, setFavoriteDoctorIds] = useState<Set<string>>(new Set());
  const [isFavoriting, setIsFavoriting] = useState(false);
  const [favoriteMessage, setFavoriteMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [comingSoonMessage, setComingSoonMessage] = useState(false);

  // Check for pre-selected specialization from URL params
  useEffect(() => {
    const specializationParam = searchParams.get('specialization');
    
    if (specializationParam && specializationParam !== specialization) {
      setSpecialization(specializationParam);
    }
  }, [searchParams, specialization]);

  // Auto-populate postal code from user profile
  useEffect(() => {
    if (user?.postal_code && !pincode) {
      setPincode(user.postal_code);
    }
  }, [user, pincode]);

  // Load favorite doctors if user is logged in
  useEffect(() => {
    if (user) {
      loadFavoriteDoctors();
    }
  }, [user]);

  const loadFavoriteDoctors = async () => {
    try {
      const favorites = await getFavoriteDoctors();
      const ids = new Set(favorites.map(fav => fav.doctor_id));
      setFavoriteDoctorIds(ids);
    } catch (err) {
      console.error('Failed to load favorites:', err);
    }
  };

  const handleToggleFavorite = async (doctor: Doctor) => {
    if (!user) {
      setFavoriteMessage({ type: 'error', text: 'Please log in to save favorite doctors' });
      setTimeout(() => setFavoriteMessage(null), 3000);
      return;
    }

    setIsFavoriting(true);
    const isFavorite = favoriteDoctorIds.has(doctor.id);

    try {
      if (isFavorite) {
        // Find the favorite ID and remove it
        const favorites = await getFavoriteDoctors();
        const favorite = favorites.find(fav => fav.doctor_id === doctor.id);
        if (favorite) {
          await removeFavoriteDoctor(favorite.id);
          setFavoriteDoctorIds(prev => {
            const newSet = new Set(prev);
            newSet.delete(doctor.id);
            return newSet;
          });
          setFavoriteMessage({ type: 'success', text: 'Removed from favorites' });
        }
      } else {
        // Add to favorites
        await addFavoriteDoctor({
          doctor_id: doctor.id,
          doctor_name: doctor.name,
          specialization: doctor.specialization,
          clinic_name: doctor.clinic_name,
          phone: doctor.phone,
          address: `${doctor.location.address}, ${doctor.location.city}, ${doctor.location.state} - ${doctor.location.pincode}`,
        });
        setFavoriteDoctorIds(prev => new Set(prev).add(doctor.id));
        setFavoriteMessage({ type: 'success', text: 'Added to favorites' });
      }
      setTimeout(() => setFavoriteMessage(null), 3000);
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
      setFavoriteMessage({ type: 'error', text: 'Failed to update favorites' });
      setTimeout(() => setFavoriteMessage(null), 3000);
    } finally {
      setIsFavoriting(false);
    }
  };

  // Common specializations (alphabetically sorted)
  const specializations = [
    'Cardiologist',
    'Chiropractor',
    'Dentist',
    'Dermatologist',
    'Emergency Medicine',
    'Endocrinologist',
    'ENT Specialist',
    'Family Medicine',
    'Gastroenterologist',
    'General Physician',
    'Gynecologist',
    'Internal Medicine',
    'Nephrologist',
    'Neurologist',
    'Nurse Practitioner',
    'Occupational Therapist',
    'Oncologist',
    'Ophthalmologist',
    'Optometrist',
    'Orthopedic',
    'Pediatrician',
    'Pharmacist',
    'Physical Therapist',
    'Physician Assistant',
    'Podiatrist',
    'Psychiatrist',
    'Psychologist',
    'Pulmonologist',
    'Rheumatologist',
    'Surgeon',
    'Urgent Care',
    'Urologist'
  ];

  const handleSearch = async () => {
    if (!pincode) {
      setError('Please enter a ZIP code');
      return;
    }

    setIsLoading(true);
    setError('');
    setProgress(0);
    setSearchResults(null);
    setSelectedDoctor(null);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const request: DoctorSearchRequest = {
        pincode,
        specialization: specialization || undefined, // Optional specialization
        limit: limit
      };      const response = await api.post<DoctorSearchResponse>(
        '/api/doctors/search',
        request
      );

      clearInterval(progressInterval);
      setProgress(100);

      setSearchResults(response.data);
      setCorrelationId(response.headers['x-correlation-id'] || '');

      if (response.data.doctors.length > 0) {
        setSelectedDoctor(response.data.doctors[0]);
      }

      setTimeout(() => setProgress(0), 500);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } } };
      setError(
        error.response?.data?.message || 
        'Failed to search doctors. Please try again.'
      );
      setProgress(0);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300 dark:text-gray-600'
            }`}
          />
        ))}
        <span className="ml-1 text-sm text-gray-600 dark:text-gray-400">
          {rating.toFixed(1)}
        </span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Coming Soon Toast Notification - Fixed Position */}
      {comingSoonMessage && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in-right">
          <div className="bg-blue-50 border-2 border-blue-200 text-blue-800 dark:bg-blue-900/90 dark:border-blue-700 dark:text-blue-200 rounded-lg shadow-lg p-4 max-w-md">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="font-semibold text-base">Book Appointment - Coming Soon! 🏥</p>
                <p className="text-sm mt-1">We're working on this feature. Stay tuned for updates!</p>
              </div>
              <button
                onClick={() => setComingSoonMessage(false)}
                className="flex-shrink-0 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {progress > 0 && (
        <div className="fixed top-0 left-0 w-full h-1 bg-gray-200 dark:bg-gray-700 z-50">
          <div
            className="h-full bg-blue-600 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Find Nearby Doctors
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Search for recommended doctors based on your location and required specialization
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {/* PIN Code Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <MapPin className="inline w-4 h-4 mr-1" />
                PIN Code
              </label>
              <input
                type="text"
                value={pincode}
                onChange={(e) => setPincode(e.target.value)}
                placeholder="Enter PIN code (e.g., 560001)"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                         focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                maxLength={10}
              />
            </div>

            {/* Specialization Select */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Filter className="inline w-4 h-4 mr-1" />
                Specialization <span className="text-gray-500 dark:text-gray-400 text-xs">(Optional)</span>
              </label>
              <select
                value={specialization}
                onChange={(e) => setSpecialization(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                         focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Specializations</option>
                {specializations.map((spec) => (
                  <option key={spec} value={spec}>
                    {spec}
                  </option>
                ))}
              </select>
            </div>

            {/* Result Limit */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Results
              </label>
              <input
                type="number"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                min="1"
                max="200"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                         focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Default: 50, Maximum: 200
              </p>
            </div>
          </div>

          {/* Search Button */}
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="w-full md:w-auto px-6 py-2 bg-blue-600 hover:bg-blue-700 
                     disabled:bg-gray-400 text-white rounded-lg transition-colors
                     flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <LoadingSpinner size="sm" />
                Searching...
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                Search Doctors
              </>
            )}
          </button>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 
                          dark:border-red-800 rounded-lg">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}
        </div>

        {/* Results */}
        {searchResults && (
          <div>
            {/* Favorite Message */}
            {favoriteMessage && (
              <div className={`mb-4 p-4 rounded-lg border ${
                favoriteMessage.type === 'success'
                  ? 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400'
                  : 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400'
              }`}>
                {favoriteMessage.text}
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Doctor List */}
            <div className="lg:col-span-1 space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  Found {searchResults.total_doctors_found} Doctor{searchResults.total_doctors_found !== 1 ? 's' : ''}
                </h2>
                
                {searchResults.doctors.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-400 mb-4">
                      <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      No Doctors Available
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      {searchResults.specialization ? (
                        <>No doctors with specialization "{searchResults.specialization}" found in ZIP code {searchResults.user_location.pincode}.</>
                      ) : (
                        <>No doctors found in ZIP code {searchResults.user_location.pincode}.</>
                      )}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      Try searching with a different ZIP code{searchResults.specialization ? ' or specialization' : ''}.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[600px] overflow-y-auto">
                    {searchResults.doctors.map((doctor) => (
                    <div
                      key={doctor.id}
                      onClick={() => setSelectedDoctor(doctor)}
                      className={`p-4 border rounded-lg cursor-pointer transition-all ${
                        selectedDoctor?.id === doctor.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                      }`}
                    >
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {doctor.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {doctor.specialization}
                      </p>
                      <div className="flex items-center mt-2">
                        {renderStars(doctor.rating)}
                      </div>
                    </div>
                  ))}
                  </div>
                )}
              </div>
            </div>

            {/* Map and Details */}
            <div className="lg:col-span-2 space-y-4">
              {/* Map View */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Interactive Map
                </h2>
                <DoctorMap
                  doctors={searchResults.doctors.map(doc => ({
                    id: doc.id,
                    name: doc.name,
                    latitude: doc.location.latitude,
                    longitude: doc.location.longitude,
                    city: doc.location.city,
                    state: doc.location.state,
                    distance: doc.distance_km,
                    isSelected: selectedDoctor?.id === doc.id
                  }))}
                  userLocation={{
                    latitude: searchResults.user_location.latitude,
                    longitude: searchResults.user_location.longitude,
                    address: searchResults.user_location.address
                  }}
                  onDoctorSelect={(doctorId: string) => {
                    const doctor = searchResults.doctors.find(d => d.id === doctorId);
                    if (doctor) setSelectedDoctor(doctor);
                  }}
                />
              </div>

              {/* Doctor Details */}
              {selectedDoctor && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                    {selectedDoctor.name}
                  </h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Specialization</p>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {selectedDoctor.specialization}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Qualification</p>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {selectedDoctor.qualification}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Experience</p>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {selectedDoctor.experience_years} years
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Rating</p>
                        {renderStars(selectedDoctor.rating)}
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Clinic</p>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {selectedDoctor.clinic_name}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                          <MapPin className="inline w-4 h-4 mr-1" />
                          Address
                        </p>
                        <p className="text-gray-700 dark:text-gray-300">
                          {selectedDoctor.location.address}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {selectedDoctor.location.city}, {selectedDoctor.location.state} - {selectedDoctor.location.pincode}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                          <Phone className="inline w-4 h-4 mr-1" />
                          Phone
                        </p>
                        <a
                          href={`tel:${selectedDoctor.phone}`}
                          className="text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          {selectedDoctor.phone}
                        </a>
                      </div>
                      
                      {selectedDoctor.email && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                            <Mail className="inline w-4 h-4 mr-1" />
                            Email
                          </p>
                          <a
                            href={`mailto:${selectedDoctor.email}`}
                            className="text-blue-600 dark:text-blue-400 hover:underline"
                          >
                            {selectedDoctor.email}
                          </a>
                        </div>
                      )}
                      
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                          <Clock className="inline w-4 h-4 mr-1" />
                          Available
                        </p>
                        <p className="text-gray-700 dark:text-gray-300">
                          {selectedDoctor.available_days.join(', ')}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {selectedDoctor.available_hours}
                        </p>
                      </div>
                      
                      {selectedDoctor.consultation_fee && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Consultation Fee</p>
                          <p className="text-lg font-semibold text-green-600 dark:text-green-400">
                            ₹{selectedDoctor.consultation_fee}
                          </p>
                        </div>
                      )}
                      
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Languages</p>
                        <p className="text-gray-700 dark:text-gray-300">
                          {selectedDoctor.languages.join(', ')}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-6 flex gap-4">
                    <button
                      onClick={() => handleToggleFavorite(selectedDoctor)}
                      disabled={isFavoriting}
                      className={`px-6 py-3 rounded-lg transition-colors font-medium flex items-center gap-2
                                 ${favoriteDoctorIds.has(selectedDoctor.id)
                                   ? 'bg-red-100 hover:bg-red-200 text-red-700 dark:bg-red-900/30 dark:hover:bg-red-900/50 dark:text-red-400'
                                   : 'bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300'
                                 } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      <Heart 
                        className={`w-5 h-5 ${favoriteDoctorIds.has(selectedDoctor.id) ? 'fill-current' : ''}`}
                      />
                      {favoriteDoctorIds.has(selectedDoctor.id) ? 'Saved' : 'Save'}
                    </button>
                    <button 
                      onClick={() => {
                        setComingSoonMessage(true);
                        setTimeout(() => setComingSoonMessage(false), 5000);
                      }}
                      className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white 
                                     rounded-lg transition-colors font-medium">
                      Book Appointment
                    </button>
                    <button 
                      onClick={() => {
                        if (!selectedDoctor) return;
                        
                        const { latitude, longitude, address, city, state } = selectedDoctor.location;
                        const destination = `${latitude},${longitude}`;
                        const label = encodeURIComponent(`${selectedDoctor.name}, ${address}, ${city}, ${state}`);
                        
                        // Detect device and open appropriate maps app
                        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
                        const isAndroid = /Android/.test(navigator.userAgent);
                        
                        if (isIOS) {
                          // iOS: Try Apple Maps first, fallback to Google Maps
                          const appleMapsUrl = `maps://maps.apple.com/?daddr=${destination}&q=${label}`;
                          window.location.href = appleMapsUrl;
                          
                          // Fallback to Google Maps if Apple Maps doesn't open
                          setTimeout(() => {
                            const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${destination}`;
                            window.open(googleMapsUrl, '_blank');
                          }, 500);
                        } else if (isAndroid) {
                          // Android: Open Google Maps with exact coordinates
                          const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${destination}`;
                          window.location.href = googleMapsUrl;
                        } else {
                          // Desktop: Open Google Maps in new tab with exact coordinates
                          const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${destination}`;
                          window.open(googleMapsUrl, '_blank');
                        }
                      }}
                      className="flex-1 px-6 py-3 bg-gray-200 hover:bg-gray-300 
                                     dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 
                                     dark:text-white rounded-lg transition-colors font-medium
                                     flex items-center justify-center gap-2">
                      <Navigation className="w-5 h-5" />
                      Get Directions
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          </div>
        )}

        {/* Correlation ID */}
        {correlationId && (
          <div className="mt-4 text-center text-xs text-gray-500 dark:text-gray-400">
            Request ID: {correlationId}
          </div>
        )}
      </div>
    </div>
  );
}

export default function DoctorFinderPage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <DoctorFinderContent />
    </Suspense>
  );
}
