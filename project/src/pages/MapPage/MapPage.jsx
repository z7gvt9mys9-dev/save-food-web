import React, { useState, useEffect, useCallback } from 'react';
import './MapPage.css';
import { MapPin, Package, AlertCircle, Navigation, Loader, MapIcon, AlertTriangle } from 'lucide-react';
import { YMaps, Map as YandexMap, Placemark, Polyline, ZoomControl, FullscreenControl } from 'react-yandex-maps';
import { projectsAPI, routingAPI } from '../../services/api';

// Red Square coordinates (Moscow)
const RED_SQUARE = [55.7536, 37.6201];

// =====================
// COMPONENT
// =====================
const MapPage = () => {
  const [mapState, setMapState] = useState({
    center: RED_SQUARE,
    zoom: 12
  });

  const [projects, setProjects] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState(null);
  const [userLocation, setUserLocation] = useState(RED_SQUARE);
  const [route, setRoute] = useState(null);
  const [routeLoading, setRouteLoading] = useState(false);

  // =====================
  // FETCH PROJECTS
  // =====================
  const fetchProjects = useCallback(async () => {
    try {
      setProjectsLoading(true);
      const res = await fetch('http://localhost:5000/api/projects');
      const data = await res.json();
      setProjects(data || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
      setProjects([]);
    } finally {
      setProjectsLoading(false);
    }
  }, []);

  // Initialize on mount - fetch projects and get user location
  useEffect(() => {
    let isMounted = true;

    const initialize = async () => {
      try {
        setProjectsLoading(true);
        const res = await fetch('http://localhost:5000/api/projects');
        const data = await res.json();
        if (isMounted) {
          setProjects(data || []);
        }
      } catch (err) {
        console.error('Failed to fetch projects:', err);
        if (isMounted) {
          setProjects([]);
        }
      } finally {
        if (isMounted) {
          setProjectsLoading(false);
        }
      }

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const userLoc = [position.coords.latitude, position.coords.longitude];
            if (isMounted) {
              setUserLocation(userLoc);
              setMapState({
                center: userLoc,
                zoom: 14,
              });
              console.log('[Map] User location detected:', userLoc);
            }
          },
          (error) => {
            console.warn('[Map] Geolocation denied/unavailable, using Moscow Red Square:', error);
            // Stay with RED_SQUARE default
            if (isMounted) {
              setUserLocation(RED_SQUARE);
            }
          }
        );
      } else {
        console.warn('[Map] Geolocation not supported, using Moscow Red Square');
        // Browser doesn't support geolocation - stay with defaults
        if (isMounted) {
          setUserLocation(RED_SQUARE);
        }
      }
    };

    initialize();
    return () => {
      isMounted = false;
    };
  }, []); // Empty deps - run only once on mount

  // =====================
  // DISTANCE CALCULATION
  // =====================
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return (R * c).toFixed(1);
  };

  // =====================
  // BUILD ROUTE
  // =====================
  const buildRoute = async (project) => {
    try {
      setRouteLoading(true);
      
      const locations = [
        {
          id: 'start',
          lat: userLocation[0],
          lon: userLocation[1],
          name: 'Your Location',
          type: 'start'
        },
        {
          id: String(project.id),
          lat: project.latitude,
          lon: project.longitude,
          name: project.name,
          type: 'end'
        }
      ];

      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Route timeout')), 4000)
      );
      
      const routeData = await Promise.race([
        routingAPI.getRoute(locations),
        timeoutPromise
      ]);
      
      if (routeData && routeData.coordinates) {
        setRoute({
          coordinates: routeData.coordinates,
          distance: (routeData.distance / 1000).toFixed(2),
          duration: Math.round(routeData.duration / 60),
          project: project
        });
      } else {
        setRoute({
          coordinates: [userLocation, [project.latitude, project.longitude]],
          distance: calculateDistance(userLocation[0], userLocation[1], project.latitude, project.longitude),
          duration: '...',
          project: project
        });
      }
    } catch (err) {
      setRoute({
        coordinates: [userLocation, [project.latitude, project.longitude]],
        distance: calculateDistance(userLocation[0], userLocation[1], project.latitude, project.longitude),
        duration: '...',
        project: project
      });
    } finally {
      setRouteLoading(false);
    }
  };

  const renderRoute = () => {
    if (!route || !route.coordinates) return null;

    return (
      <Polyline
        key="route-polyline"
        geometry={route.coordinates}
        options={{
          strokeColor: '#FF6B35',
          strokeWidth: 3,
          opacity: 0.8,
          strokeStyle: 'solid'
        }}
      />
    );
  };

  return (
    <div className="map-container">
      <div className="projects-panel">
        <h3>Projects Nearby</h3>
        {projectsLoading ? (
          <div className="loading">
            <Loader size={16} className="spinner" />
            Loading projects...
          </div>
        ) : projects.length === 0 ? (
          <div className="empty">No projects found</div>
        ) : (
          <div className="projects-list">
            {projects.map((project) => {
              const distance = calculateDistance(
                mapState.center[0],
                mapState.center[1],
                project.latitude,
                project.longitude
              );
              return (
                <div
                  key={project.id}
                  className="project-item"
                  onClick={() => {
                    setMapState({
                      center: [project.latitude, project.longitude],
                      zoom: 15
                    });
                    setSelectedProject(project);
                    buildRoute(project);
                  }}
                >
                  <div className="project-icon">{project.icon || ''}</div>
                  <div className="project-info">
                    <div className="project-name">{project.name}</div>
                    <div className="project-distance">{distance} км</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <YMaps query={{ lang: 'ru_RU' }}>
        <YandexMap
          state={mapState}
          width="100%"
          height="100%"
          options={{ suppressMapOpenBlock: true }}
        >
          <ZoomControl />
          <FullscreenControl />

          {renderRoute()}

          <Placemark
            geometry={userLocation}
            options={{ preset: 'islands#blueCircleDotIcon', iconColor: '#3498db' }}
            properties={{
              name: 'Your Location',
              description: 'Starting point'
            }}
          />

          {projects.map((project) => (
            <Placemark
              key={project.id}
              geometry={[project.latitude, project.longitude]}
              options={{ 
                preset: 'islands#redIcon',
                iconColor: selectedProject?.id === project.id ? '#FF6B35' : '#4ECDC4',
                onClick: () => {
                  setSelectedProject(project);
                  buildRoute(project);
                }
              }}
              properties={{
                balloonContent: `<div><strong>${project.name}</strong></div>`
              }}
            />
          ))}
        </YandexMap>
      </YMaps>

      {route && (
        <div className="route-info-panel">
          <div className="route-header">
            <Navigation size={20} />
            <h3>Route to {route.project.name}</h3>
          </div>
          <div className="route-details">
            <div className="route-detail">
              <span className="label">Distance:</span>
              <span className="value">{route.distance} km</span>
            </div>
            <div className="route-detail">
              <span className="label">Duration:</span>
              <span className="value">{route.duration} min</span>
            </div>
          </div>
          {routeLoading && (
            <div className="route-loading">
              <Loader size={16} className="spinner" />
              Calculating route...
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MapPage;
