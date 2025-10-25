'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Heart, MapPin, Phone, Mail, Clock, Calendar, Trash2, Edit, Navigation, Users } from 'lucide-react';
import { getFavoriteDoctors, removeFavoriteDoctor, updateFavoriteDoctor } from '@/lib/api-client';
import { FavoriteDoctor } from '@/types/doctors';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import ProtectedRoute from '@/components/shared/ProtectedRoute';

function FavoriteDoctorsContent() {
  const [favorites, setFavorites] = useState<FavoriteDoctor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editNotes, setEditNotes] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      setIsLoading(true);
      const data = await getFavoriteDoctors();
      setFavorites(data);
      setError('');
    } catch (err) {
      console.error('Failed to load favorites:', err);
      setError('Failed to load favorite doctors');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (favoriteId: number) => {
    if (!confirm('Are you sure you want to remove this doctor from favorites?')) {
      return;
    }

    try {
      setDeletingId(favoriteId);
      await removeFavoriteDoctor(favoriteId);
      setFavorites(prev => prev.filter(fav => fav.id !== favoriteId));
      showMessage('success', 'Removed from favorites');
    } catch (err) {
      console.error('Failed to delete favorite:', err);
      showMessage('error', 'Failed to remove favorite');
    } finally {
      setDeletingId(null);
    }
  };

  const handleStartEdit = (favorite: FavoriteDoctor) => {
    setEditingId(favorite.id);
    setEditNotes(favorite.notes || '');
  };

  const handleSaveEdit = async (favoriteId: number) => {
    try {
      const updated = await updateFavoriteDoctor(favoriteId, { notes: editNotes });
      setFavorites(prev => prev.map(fav => fav.id === favoriteId ? updated : fav));
      setEditingId(null);
      showMessage('success', 'Notes updated');
    } catch (err) {
      console.error('Failed to update notes:', err);
      showMessage('error', 'Failed to update notes');
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditNotes('');
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
                <Heart className="w-8 h-8 text-red-500 fill-current" />
                My Favorite Doctors
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Manage your saved doctors and appointments
              </p>
            </div>
            <Link
              href="/doctors"
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                       transition-colors font-medium flex items-center gap-2 shadow-md"
            >
              <Users className="w-5 h-5" />
              Find Doctors
            </Link>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg border ${
            message.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400'
              : 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400'
          }`}>
            {message.text}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 
                        rounded-lg p-6 text-center">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <button
              onClick={loadFavorites}
              className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!error && favorites.length === 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center">
            <Heart className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              No Favorite Doctors Yet
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Start adding doctors to your favorites from the doctor finder page
            </p>
            <a
              href="/doctors"
              className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white 
                       rounded-lg transition-colors font-medium"
            >
              Find Doctors
            </a>
          </div>
        )}

        {/* Favorites List */}
        {!error && favorites.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {favorites.map((favorite) => (
              <div
                key={favorite.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg 
                         transition-shadow border border-gray-200 dark:border-gray-700"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
                      {favorite.doctor_name}
                    </h3>
                    <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                      {favorite.specialization}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(favorite.id)}
                    disabled={deletingId === favorite.id}
                    className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 
                             rounded-lg transition-colors disabled:opacity-50"
                    title="Remove from favorites"
                  >
                    {deletingId === favorite.id ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Trash2 className="w-5 h-5" />
                    )}
                  </button>
                </div>

                {/* Details */}
                <div className="space-y-3 mb-4">
                  {favorite.clinic_name && (
                    <div className="flex items-start gap-2">
                      <MapPin className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                      <div className="text-sm">
                        <p className="font-medium text-gray-900 dark:text-white">
                          {favorite.clinic_name}
                        </p>
                        {favorite.address && (
                          <p className="text-gray-600 dark:text-gray-400 mt-1">
                            {favorite.address}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {favorite.phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-gray-500 flex-shrink-0" />
                      <a
                        href={`tel:${favorite.phone}`}
                        className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        {favorite.phone}
                      </a>
                    </div>
                  )}

                  {favorite.last_visit && (
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-gray-500 flex-shrink-0" />
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Last visit: {new Date(favorite.last_visit).toLocaleDateString()}
                      </p>
                    </div>
                  )}

                  {favorite.next_appointment && (
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-500 flex-shrink-0" />
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Next: {new Date(favorite.next_appointment).toLocaleDateString()}
                      </p>
                    </div>
                  )}
                </div>

                {/* Notes Section */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                  {editingId === favorite.id ? (
                    <div className="space-y-2">
                      <textarea
                        value={editNotes}
                        onChange={(e) => setEditNotes(e.target.value)}
                        placeholder="Add notes..."
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 
                                 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 
                                 dark:bg-gray-700 dark:text-white"
                        rows={3}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSaveEdit(favorite.id)}
                          className="flex-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white 
                                   rounded text-sm font-medium"
                        >
                          Save
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="flex-1 px-3 py-1.5 bg-gray-200 hover:bg-gray-300 
                                   dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 
                                   dark:text-white rounded text-sm font-medium"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                          Notes
                        </p>
                        <button
                          onClick={() => handleStartEdit(favorite)}
                          className="p-1 text-gray-600 hover:text-blue-600 dark:text-gray-400 
                                   dark:hover:text-blue-400 transition-colors"
                          title="Edit notes"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {favorite.notes || 'No notes added'}
                      </p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                {favorite.address && (
                  <button
                    onClick={() => {
                      // Open in maps
                      const address = encodeURIComponent(favorite.address || '');
                      window.open(`https://www.google.com/maps/search/?api=1&query=${address}`, '_blank');
                    }}
                    className="mt-4 w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 
                             dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 
                             dark:text-white rounded-lg transition-colors font-medium 
                             flex items-center justify-center gap-2"
                  >
                    <Navigation className="w-4 h-4" />
                    Get Directions
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Footer Stats */}
        {!error && favorites.length > 0 && (
          <div className="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
            You have {favorites.length} favorite doctor{favorites.length !== 1 ? 's' : ''} saved
          </div>
        )}
      </div>
    </div>
  );
}

export default function FavoriteDoctorsPage() {
  return (
    <ProtectedRoute>
      <FavoriteDoctorsContent />
    </ProtectedRoute>
  );
}
