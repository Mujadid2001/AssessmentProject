/**
 * API client for ELD backend
 * Handles all HTTP communication with Django REST API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class APIClient {
  /**
   * Generate HOS logs for a trip
   * @param {Object} payload - Request data
   * @returns {Promise<Object>} - Generated logs and cycle state
   */
  async generateLogs(payload) {
    const response = await fetch(`${API_BASE_URL}/logs/generate_logs/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to generate logs');
    }

    return response.json();
  }

  /**
   * Get driver cycle status
   * @param {number} driverId - Driver ID
   * @returns {Promise<Object>} - Cycle state
   */
  async getDriverCycleStatus(driverId) {
    const response = await fetch(`${API_BASE_URL}/drivers/${driverId}/cycle_status/`);

    if (!response.ok) {
      throw new Error('Failed to fetch driver status');
    }

    return response.json();
  }

  /**
   * Get driver logs
   * @param {number} driverId - Driver ID
   * @returns {Promise<Array>} - Array of logs
   */
  async getDriverLogs(driverId) {
    const response = await fetch(`${API_BASE_URL}/logs/?driver_id=${driverId}`);

    if (!response.ok) {
      throw new Error('Failed to fetch logs');
    }

    const data = await response.json();
    return data.results || [];
  }

  /**
   * Create a trip
   * @param {Object} tripData - Trip data
   * @returns {Promise<Object>} - Created trip
   */
  async createTrip(tripData) {
    const response = await fetch(`${API_BASE_URL}/trips/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tripData),
    });

    if (!response.ok) {
      throw new Error('Failed to create trip');
    }

    return response.json();
  }

  /**
   * Health check
   * @returns {Promise<Object>} - Health status
   */
  async healthCheck() {
    const baseUrl = API_BASE_URL.split('/api')[0];
    const response = await fetch(`${baseUrl}/api/health/`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }
}

export const apiClient = new APIClient();
