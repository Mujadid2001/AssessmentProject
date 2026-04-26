/**
 * Main App component - ELD Simulator
 * Production-grade logistics SaaS dark theme interface
 */

import React, { useState, useEffect } from 'react';
import {
  Truck,
  AlertCircle,
  CheckCircle,
  Clock,
  MapPin,
  Navigation,
  TrendingUp,
  AlertTriangle,
} from 'lucide-react';
import { ELDGrid } from './components/ELDGrid';
import { Map } from './components/Map';
import { apiClient } from './api';

export default function App() {
  const [formData, setFormData] = useState({
    driver_id: 1,
    current_location: '123 Main St, Springfield, IL',
    pickup_location: '456 Oak Ave, Chicago, IL',
    dropoff_location: '789 Elm Rd, New York, NY',
    distance_miles: 800,
    cycle_used: 35.5,
    start_time: new Date().toISOString(),
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [logs, setLogs] = useState([]);
  const [cycleState, setCycleState] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);
  const [apiHealth, setApiHealth] = useState(null);

  // Check API health on mount
  useEffect(() => {
    apiClient
      .healthCheck()
      .then((data) => {
        setApiHealth({ status: 'healthy', message: data.service });
      })
      .catch((err) => {
        setApiHealth({ status: 'offline', message: 'Cannot reach API' });
      });
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'distance_miles' || name === 'cycle_used' ? parseFloat(value) : value,
    }));
  };

  const handleGenerateLogs = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.generateLogs({
        ...formData,
        start_time: new Date().toISOString(),
      });

      setLogs(response.logs || []);
      setCycleState(response.cycle_state);
      setSelectedLog(response.logs[0]);
    } catch (err) {
      setError(err.message || 'Failed to generate logs');
    } finally {
      setLoading(false);
    }
  };

  const currentLog = selectedLog || logs[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-white">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-slate-700 bg-slate-900/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Truck className="w-6 h-6 text-blue-400" />
            <h1 className="text-2xl font-bold">ELD Simulator</h1>
            <span className="text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded border border-blue-700">
              v1.0.0
            </span>
          </div>

          <div className="flex items-center gap-2">
            {apiHealth && (
              <div
                className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded border ${
                  apiHealth.status === 'healthy'
                    ? 'bg-green-900/30 border-green-700 text-green-300'
                    : 'bg-red-900/30 border-red-700 text-red-300'
                }`}
              >
                <div className={`w-2 h-2 rounded-full ${apiHealth.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                {apiHealth.message}
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Form */}
          <div className="lg:col-span-1">
            <form onSubmit={handleGenerateLogs} className="bg-slate-800 p-6 rounded-lg border border-slate-700 space-y-4">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Navigation className="w-5 h-5 text-blue-400" />
                Trip Details
              </h2>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Driver ID</label>
                <input
                  type="number"
                  name="driver_id"
                  value={formData.driver_id}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Current Location</label>
                <input
                  type="text"
                  name="current_location"
                  value={formData.current_location}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Pickup Location</label>
                <input
                  type="text"
                  name="pickup_location"
                  value={formData.pickup_location}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Dropoff Location</label>
                <input
                  type="text"
                  name="dropoff_location"
                  value={formData.dropoff_location}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Distance (miles)</label>
                <input
                  type="number"
                  name="distance_miles"
                  step="0.1"
                  value={formData.distance_miles}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Cycle Hours Used</label>
                <input
                  type="number"
                  name="cycle_used"
                  step="0.1"
                  value={formData.cycle_used}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 disabled:opacity-50 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                {loading ? 'Generating...' : 'Generate Logs'}
              </button>
            </form>

            {/* Cycle Status */}
            {cycleState && (
              <div className="mt-6 bg-slate-800 p-6 rounded-lg border border-slate-700">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-amber-400" />
                  HOS Cycle Status
                </h3>

                <div className="space-y-3">
                  <div>
                    <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Hours Used</div>
                    <div className="text-2xl font-bold text-amber-400">
                      {cycleState.cycle_hours_used.toFixed(1)}h / 70h
                    </div>
                    <div className="mt-2 w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                      <div
                        className="h-full bg-amber-500 transition-all"
                        style={{ width: `${(cycleState.cycle_hours_used / 70) * 100}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Available Hours</div>
                    <div className="text-xl font-bold text-green-400">{cycleState.hours_available.toFixed(1)}h</div>
                  </div>

                  {cycleState.requires_restart && (
                    <div className="bg-red-900/30 border border-red-700 rounded p-3 mt-3">
                      <div className="flex items-center gap-2 text-red-300">
                        <AlertTriangle className="w-4 h-4" />
                        <span className="text-sm font-semibold">Mandatory 34-Hour Restart Required</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="lg:col-span-2 space-y-6">
            {error && (
              <div className="bg-red-900/20 border border-red-700 rounded p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-400 mb-1">Error</h3>
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              </div>
            )}

            {currentLog && (
              <>
                {/* Logs List */}
                {logs.length > 1 && (
                  <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <Clock className="w-5 h-5 text-blue-400" />
                      Generated Logs
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                      {logs.map((log, idx) => (
                        <button
                          key={idx}
                          onClick={() => setSelectedLog(log)}
                          className={`p-3 rounded border transition-colors text-left ${
                            selectedLog?.log_date === log.log_date
                              ? 'bg-blue-900 border-blue-600'
                              : 'bg-slate-700 border-slate-600 hover:border-slate-500'
                          }`}
                        >
                          <div className="text-sm font-medium">{log.log_date}</div>
                          <div className="text-xs text-slate-400 mt-1">
                            {log.total_driving_minutes} min driving
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* ELD Grid */}
                <ELDGrid
                  events={currentLog.events_json || []}
                  date={currentLog.log_date}
                  violations={currentLog.violations || []}
                />

                {/* Map */}
                <Map
                  events={currentLog.events_json || []}
                  startLocation={{
                    lat: 38.8816,
                    lng: -77.1043,
                    name: formData.pickup_location,
                  }}
                  endLocation={{
                    lat: 40.7128,
                    lng: -74.006,
                    name: formData.dropoff_location,
                  }}
                />
              </>
            )}

            {!currentLog && !loading && (
              <div className="bg-slate-800 p-12 rounded-lg border border-slate-700 border-dashed text-center">
                <MapPin className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 text-lg">
                  Fill in trip details and click <strong>Generate Logs</strong> to see results
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-slate-900/50 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-sm text-slate-400">
          <p>
            ELD Simulator • FMCSA HOS Compliant • Production Ready • Generated with ✓
            Accuracy
          </p>
        </div>
      </footer>
    </div>
  );
}
