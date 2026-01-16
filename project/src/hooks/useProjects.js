import { useState, useEffect, useCallback } from 'react';

export const useProjects = (
  userId = undefined,
  apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'
) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const endpoint = userId ? `/projects?userId=${userId}` : '/projects';
      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || 
          errorData.error || 
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();

      let projectsArray = Array.isArray(data) ? data : (data?.projects || data?.data || []);

      if (!Array.isArray(projectsArray)) {
        projectsArray = [];
      }

      setProjects(projectsArray);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load projects: ${errorMessage}`);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  }, [userId, apiBaseUrl]);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return {
    projects,
    loading,
    error,
    refetch: fetchProjects,
  };
};

export const useNearbyProjects = (
  latitude = 55.7536,
  longitude = 37.6201,
  radiusKm = 50,
  apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'
) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchNearbyProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const params = new URLSearchParams({
        latitude: latitude.toString(),
        longitude: longitude.toString(),
        radius_km: radiusKm.toString(),
      });

      const response = await fetch(
        `${apiBaseUrl}/projects/nearby/all?${params}`,
        {
          method: 'GET',
          headers,
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail ||
          errorData.error ||
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      let projectsArray = Array.isArray(data) ? data : (data?.projects || data?.data || []);

      if (!Array.isArray(projectsArray)) {
        projectsArray = [];
      }

      setProjects(projectsArray);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load nearby projects: ${errorMessage}`);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  }, [latitude, longitude, radiusKm, apiBaseUrl]);

  useEffect(() => {
    fetchNearbyProjects();
  }, [fetchNearbyProjects]);

  return {
    projects,
    loading,
    error,
    refetch: fetchNearbyProjects,
  };
};

export const useAllProjects = (
  apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'
) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAllProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${apiBaseUrl}/projects`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || 
          errorData.error || 
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();

      let projectsArray = Array.isArray(data) ? data : (data?.projects || data?.data || []);

      if (!Array.isArray(projectsArray)) {
        projectsArray = [];
      }

      setProjects(projectsArray);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load all projects: ${errorMessage}`);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  }, [apiBaseUrl]);

  useEffect(() => {
    fetchAllProjects();
  }, [fetchAllProjects]);

  return {
    projects,
    loading,
    error,
    refetch: fetchAllProjects,
  };
};
