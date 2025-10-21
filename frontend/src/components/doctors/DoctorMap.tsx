'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface DoctorLocation {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  city: string;
  state: string;
  distance: number;
  isSelected: boolean;
}

interface DoctorMapProps {
  doctors: DoctorLocation[];
  userLocation: {
    latitude: number;
    longitude: number;
    address: string;
  };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onDoctorSelect: any;
}

export default function DoctorMap({ doctors, userLocation, onDoctorSelect }: DoctorMapProps) {
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);

  useEffect(() => {
    // Initialize map only once
    if (!mapRef.current) {
      mapRef.current = L.map('doctor-map').setView(
        [userLocation.latitude, userLocation.longitude],
        10
      );

      // Add OpenStreetMap tiles (free, no API key needed)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(mapRef.current);

      // Add user location marker
      const userIcon = L.divIcon({
        html: `
          <div style="
            width: 32px;
            height: 32px;
            background: #3B82F6;
            border: 4px solid white;
            border-radius: 50%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
          ">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
              <circle cx="12" cy="12" r="8"/>
            </svg>
          </div>
        `,
        className: '',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      L.marker([userLocation.latitude, userLocation.longitude], { icon: userIcon })
        .bindPopup(`<b>Your Location</b><br>${userLocation.address}`)
        .addTo(mapRef.current);
    }

    // Clear existing doctor markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add doctor markers with slight offset to avoid stacking
    doctors.forEach((doctor, index) => {
      if (!mapRef.current) return;

      const isSelected = doctor.isSelected;
      
      // Add small random offset to prevent exact overlap
      // Offset is about 0.01 degrees (~1km) in a circular pattern
      const angle = (index * 2 * Math.PI) / doctors.length;
      const radius = 0.015 + (index % 3) * 0.005; // Variable radius for better spread
      const latOffset = Math.cos(angle) * radius;
      const lonOffset = Math.sin(angle) * radius;
      
      const adjustedLat = doctor.latitude + latOffset;
      const adjustedLon = doctor.longitude + lonOffset;
      
      const doctorIcon = L.divIcon({
        html: `
          <div style="
            width: ${isSelected ? '44px' : '36px'};
            height: ${isSelected ? '44px' : '36px'};
            background: ${isSelected ? '#3B82F6' : '#EF4444'};
            border: ${isSelected ? '5px solid #93C5FD' : '3px solid white'};
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            z-index: ${isSelected ? '1000' : '500'};
          ">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
        `,
        className: `doctor-marker ${isSelected ? 'selected' : ''}`,
        iconSize: [isSelected ? 44 : 36, isSelected ? 44 : 36],
        iconAnchor: [isSelected ? 22 : 18, isSelected ? 44 : 36],
      });

      const marker = L.marker([adjustedLat, adjustedLon], { icon: doctorIcon })
        .bindPopup(`
          <div style="min-width: 200px;">
            <b style="font-size: 14px; color: #1F2937;">${doctor.name}</b><br>
            <span style="font-size: 12px; color: #6B7280;">${doctor.city}, ${doctor.state}</span><br>
            <span style="font-size: 12px; color: #3B82F6; font-weight: 600;">${doctor.distance.toFixed(1)} km away</span>
          </div>
        `)
        .addTo(mapRef.current);

      marker.on('click', () => {
        onDoctorSelect(doctor.id);
      });

      // Open popup for selected doctor
      if (isSelected) {
        marker.openPopup();
      }

      markersRef.current.push(marker);
    });

    // Fit map to show all markers or zoom to selected doctor
    const selectedDoctor = doctors.find(d => d.isSelected);
    
    if (selectedDoctor) {
      // Zoom to selected doctor with offset
      const angle = doctors.indexOf(selectedDoctor) * 2 * Math.PI / doctors.length;
      const radius = 0.015 + (doctors.indexOf(selectedDoctor) % 3) * 0.005;
      const latOffset = Math.cos(angle) * radius;
      const lonOffset = Math.sin(angle) * radius;
      
      mapRef.current?.setView(
        [selectedDoctor.latitude + latOffset, selectedDoctor.longitude + lonOffset],
        13,
        { animate: true }
      );
    } else if (doctors.length > 0) {
      // Fit all markers
      const bounds = L.latLngBounds(
        doctors.map(d => [d.latitude, d.longitude])
      );
      bounds.extend([userLocation.latitude, userLocation.longitude]);
      mapRef.current?.fitBounds(bounds, { padding: [50, 50] });
    }

  }, [doctors, userLocation, onDoctorSelect]);

  return (
    <div className="relative">
      <div 
        id="doctor-map" 
        className="w-full h-96 rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600"
        style={{ zIndex: 0 }}
      />
      
      {/* Map Controls Info */}
      <div className="absolute bottom-4 left-4 bg-white dark:bg-gray-900 rounded-lg shadow-lg p-3 z-10">
        <p className="text-xs text-gray-600 dark:text-gray-400">
          🔵 Your Location | 🔴 Doctors ({doctors.length})
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
          Zoom: Scroll | Pan: Click & Drag
        </p>
      </div>
    </div>
  );
}
