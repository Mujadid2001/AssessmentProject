/**
 * Map Component - Leaflet-based route visualization
 * Renders route polyline and markers for rest/fueling stops
 */

import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Fuel, MapPin, Navigation } from 'lucide-react';

/**
 * Map Component
 * Props:
 * - events: Array of {location, status, timestamp}
 * - startLocation: {lat, lng, name}
 * - endLocation: {lat, lng, name}
 */
export const Map = ({ events = [], startLocation, endLocation }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    // Initialize map
    if (!map.current) {
      map.current = L.map(mapContainer.current).setView([39.8283, -98.5795], 4);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map.current);
    }

    // Clear existing markers and polylines
    map.current.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        map.current.removeLayer(layer);
      }
    });

    // Add start marker
    if (startLocation) {
      const greenIcon = L.icon({
        iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMxMEI5ODEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMjEgMTBjMCA3LTktMTMtOS0xM3MtOSA2LTkgMTNhOSA5IDAgMCAwIDE4IDB6Ii8+PC9zdmc+',
        iconSize: [24, 24],
        iconAnchor: [12, 24],
      });
      L.marker([startLocation.lat || 39.8283, startLocation.lng || -98.5795], { icon: greenIcon })
        .bindPopup(`<strong>Start</strong><br/>${startLocation.name || 'Current Location'}`)
        .addTo(map.current);
    }

    // Add end marker
    if (endLocation) {
      const redIcon = L.icon({
        iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNFRjQ0NDQiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMjEgMTBjMCA3LTktMTMtOS0xM3MtOSA2LTkgMTNhOSA5IDAgMCAwIDE4IDB6Ii8+PC9zdmc+',
        iconSize: [24, 24],
        iconAnchor: [12, 24],
      });
      L.marker([endLocation.lat || 40.7128, endLocation.lng || -74.0060], { icon: redIcon })
        .bindPopup(`<strong>End</strong><br/>${endLocation.name || 'Destination'}`)
        .addTo(map.current);
    }

    // Add route polyline
    if (startLocation && endLocation) {
      const route = L.polyline(
        [
          [startLocation.lat || 39.8283, startLocation.lng || -98.5795],
          [endLocation.lat || 40.7128, endLocation.lng || -74.0060],
        ],
        { color: '#3B82F6', weight: 3, opacity: 0.8 }
      );
      route.addTo(map.current);

      // Fit bounds
      map.current.fitBounds(route.getBounds(), { padding: [50, 50] });
    }

    // Add event markers (fueling, rest stops, etc.)
    const eventCounts = {};
    events.forEach((event) => {
      if (event.status === 'OFF_DUTY' || event.status === 'SLEEPER') {
        const key = event.location;
        eventCounts[key] = (eventCounts[key] || 0) + 1;

        // Simulate location (for demo purposes)
        const baseLat = 39.8283;
        const baseLng = -98.5795;
        const offset = Object.keys(eventCounts).indexOf(key) * 0.5;

        const icon = L.icon({
          iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCIgdmlld0JveD0iMCAwIDIwIDIwIiBmaWxsPSIjRjU5RTBCIj48Y2lyY2xlIGN4PSIxMCIgY3k9IjEwIiByPSI3Ii8+PC9zdmc+',
          iconSize: [20, 20],
          iconAnchor: [10, 10],
        });

        L.marker([baseLat + offset, baseLng + offset], { icon })
          .bindPopup(`<strong>${event.status}</strong><br/>${event.location}`)
          .addTo(map.current);
      }
    });
  }, [events, startLocation, endLocation]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700">
      <div className="mb-4 flex items-center gap-2">
        <Navigation className="w-5 h-5 text-blue-400" />
        <h3 className="text-lg font-bold text-white">Route Map</h3>
      </div>

      <div
        ref={mapContainer}
        className="w-full h-96 rounded border border-slate-600 bg-slate-800"
        style={{ minHeight: '400px' }}
      />

      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="flex items-center gap-2 text-green-400">
          <div className="w-4 h-4 rounded-full bg-green-500" />
          <span>Start Location</span>
        </div>
        <div className="flex items-center gap-2 text-red-400">
          <div className="w-4 h-4 rounded-full bg-red-500" />
          <span>End Location</span>
        </div>
        <div className="flex items-center gap-2 text-amber-400">
          <Fuel className="w-4 h-4" />
          <span>Fuel Stop</span>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <MapPin className="w-4 h-4" />
          <span>Rest Stop</span>
        </div>
      </div>
    </div>
  );
};
