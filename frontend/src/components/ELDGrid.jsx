/**
 * ELDGrid - High-fidelity 24-hour Electronic Log visualization
 * Renders continuous polyline across duty statuses (OFF_DUTY, SLEEPER, DRIVING, ON_DUTY)
 * SVG-based for pixel-perfect rendering like paper logbook
 */

import React, { useMemo } from 'react';
import { AlertCircle, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

const DutyStatus = {
  OFF_DUTY: 'OFF_DUTY',
  SLEEPER: 'SLEEPER',
  DRIVING: 'DRIVING',
  ON_DUTY: 'ON_DUTY',
};

const STATUS_COLORS = {
  OFF_DUTY: '#6B7280',      // Gray
  SLEEPER: '#3B82F6',       // Blue
  DRIVING: '#EF4444',       // Red
  ON_DUTY: '#F59E0B',       // Amber
};

const STATUS_LABELS = {
  OFF_DUTY: 'Off Duty',
  SLEEPER: 'Sleeper',
  DRIVING: 'Driving',
  ON_DUTY: 'On Duty',
};

/**
 * ELDGrid Component
 * Props:
 * - events: Array of {timestamp, status, location, miles, notes}
 * - date: Date string (YYYY-MM-DD)
 * - violations: Array of violation strings
 */
export const ELDGrid = ({ events = [], date = '', violations = [] }) => {
  const SVG_WIDTH = 1200;
  const SVG_HEIGHT = 400;
  const MARGIN = { top: 30, right: 30, bottom: 60, left: 60 };
  const PLOT_WIDTH = SVG_WIDTH - MARGIN.left - MARGIN.right;
  const PLOT_HEIGHT = SVG_HEIGHT - MARGIN.top - MARGIN.bottom;

  // Parse time string to minutes since midnight
  const timeToMinutes = (timestamp) => {
    try {
      const dt = new Date(timestamp);
      return dt.getHours() * 60 + dt.getMinutes();
    } catch {
      return 0;
    }
  };

  // Generate polyline points based on events
  const polylinePoints = useMemo(() => {
    if (events.length === 0) return '';

    const points = [];
    const statusToY = (status) => {
      const baseY = MARGIN.top + PLOT_HEIGHT;
      const mapping = {
        OFF_DUTY: 0.2,
        ON_DUTY: 0.4,
        DRIVING: 0.7,
        SLEEPER: 0.9,
      };
      return baseY - (mapping[status] || 0.5) * PLOT_HEIGHT;
    };

    // Normalize time across 24 hours
    for (let i = 0; i < events.length; i++) {
      const event = events[i];
      const minutes = timeToMinutes(event.timestamp);
      const x = MARGIN.left + (minutes / 1440) * PLOT_WIDTH;
      const y = statusToY(event.status);

      points.push(`${x},${y}`);
    }

    return points.join(' ');
  }, [events]);

  // Calculate statistics
  const stats = useMemo(() => {
    let drivingMinutes = 0;
    let onDutyMinutes = 0;
    let totalMiles = 0;

    events.forEach((event) => {
      if (event.status === DutyStatus.DRIVING) drivingMinutes += 30;
      if (event.status === DutyStatus.ON_DUTY) onDutyMinutes += 30;
      totalMiles += event.miles || 0;
    });

    return {
      drivingHours: (drivingMinutes / 60).toFixed(1),
      onDutyHours: (onDutyMinutes / 60).toFixed(1),
      totalMiles: totalMiles.toFixed(0),
    };
  }, [events]);

  // Render time axis labels (every 2 hours)
  const timeLabels = Array.from({ length: 13 }, (_, i) => {
    const hour = i * 2;
    const x = MARGIN.left + (hour / 24) * PLOT_WIDTH;
    return (
      <g key={`time-${i}`}>
        <line x1={x} y1={MARGIN.top + PLOT_HEIGHT} x2={x} y2={MARGIN.top + PLOT_HEIGHT + 5} stroke="#D1D5DB" />
        <text x={x} y={MARGIN.top + PLOT_HEIGHT + 20} textAnchor="middle" fontSize="12" fill="#6B7280">
          {`${hour}:00`}
        </text>
      </g>
    );
  });

  // Render status axis labels
  const statusLabels = [
    { label: 'Sleeper', y: MARGIN.top + 0.9 * PLOT_HEIGHT },
    { label: 'Driving', y: MARGIN.top + 0.7 * PLOT_HEIGHT },
    { label: 'On Duty', y: MARGIN.top + 0.4 * PLOT_HEIGHT },
    { label: 'Off Duty', y: MARGIN.top + 0.2 * PLOT_HEIGHT },
  ];

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-white mb-2">24-Hour Electronic Log</h3>
        <p className="text-sm text-slate-400">{date || 'Loading...'}</p>
      </div>

      {/* SVG Grid */}
      <div className="overflow-x-auto mb-6">
        <svg width={SVG_WIDTH} height={SVG_HEIGHT} className="bg-slate-800 rounded border border-slate-600">
          {/* Grid background */}
          <defs>
            <pattern id="grid" width="50" height="1" patternUnits="userSpaceOnUse">
              <line x1="0" y1="0" x2="0" y2={PLOT_HEIGHT} stroke="#374151" strokeWidth="0.5" />
            </pattern>
          </defs>

          {/* Grid fill */}
          <rect x={MARGIN.left} y={MARGIN.top} width={PLOT_WIDTH} height={PLOT_HEIGHT} fill="url(#grid)" />

          {/* Axes */}
          <line x1={MARGIN.left} y1={MARGIN.top} x2={MARGIN.left} y2={MARGIN.top + PLOT_HEIGHT} stroke="#9CA3AF" strokeWidth="2" />
          <line x1={MARGIN.left} y1={MARGIN.top + PLOT_HEIGHT} x2={SVG_WIDTH - MARGIN.right} y2={MARGIN.top + PLOT_HEIGHT} stroke="#9CA3AF" strokeWidth="2" />

          {/* Time labels */}
          {timeLabels}

          {/* Status labels */}
          {statusLabels.map((item, idx) => (
            <text key={`status-${idx}`} x={MARGIN.left - 10} y={item.y} textAnchor="end" fontSize="11" fill="#9CA3AF">
              {item.label}
            </text>
          ))}

          {/* Data polyline */}
          {polylinePoints && (
            <polyline
              points={polylinePoints}
              fill="none"
              stroke="#10B981"
              strokeWidth="3"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          )}

          {/* Event markers */}
          {events.map((event, idx) => {
            const minutes = timeToMinutes(event.timestamp);
            const x = MARGIN.left + (minutes / 1440) * PLOT_WIDTH;
            const statusToY = (status) => {
              const baseY = MARGIN.top + PLOT_HEIGHT;
              const mapping = {
                OFF_DUTY: 0.2,
                ON_DUTY: 0.4,
                DRIVING: 0.7,
                SLEEPER: 0.9,
              };
              return baseY - (mapping[status] || 0.5) * PLOT_HEIGHT;
            };
            const y = statusToY(event.status);

            return (
              <circle key={`marker-${idx}`} cx={x} cy={y} r="4" fill={STATUS_COLORS[event.status]} stroke="white" strokeWidth="2" />
            );
          })}
        </svg>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-800 p-4 rounded border border-slate-600">
          <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Driving Time</div>
          <div className="text-2xl font-bold text-red-400">{stats.drivingHours}h</div>
        </div>
        <div className="bg-slate-800 p-4 rounded border border-slate-600">
          <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">On Duty Time</div>
          <div className="text-2xl font-bold text-amber-400">{stats.onDutyHours}h</div>
        </div>
        <div className="bg-slate-800 p-4 rounded border border-slate-600">
          <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Total Miles</div>
          <div className="text-2xl font-bold text-green-400">{stats.totalMiles} mi</div>
        </div>
      </div>

      {/* Violations */}
      {violations.length > 0 && (
        <div className="bg-red-900 bg-opacity-20 border border-red-700 rounded p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <span className="font-semibold text-red-400">HOS Violations</span>
          </div>
          <ul className="space-y-1 text-sm text-red-300">
            {violations.map((v, i) => (
              <li key={i}>• {v}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Legend */}
      <div className="flex gap-6 text-xs mt-6">
        {Object.entries(STATUS_COLORS).map(([status, color]) => (
          <div key={status} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: color }} />
            <span className="text-slate-400">{STATUS_LABELS[status]}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
