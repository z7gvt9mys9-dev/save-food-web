import React, { useState, useEffect } from 'react';
import './MapPage.css';
import { MapPin, Package, AlertCircle, Navigation, Loader, MapIcon, AlertTriangle, Clock, Box } from 'lucide-react';
import { YMaps, Map as YandexMap, Placemark, Polyline, ZoomControl, FullscreenControl } from 'react-yandex-maps';
import { useAllProjects } from '../../hooks/useProjects';
import { useAuth } from '../../context/AuthContext';
import { routingAPI } from '../../services/api';

const RED_SQUARE = [55.7536, 37.6201];

const MapPage = () => {
  const { projects, loading: projectsLoading } = useAllProjects();
  const { showToast } = useAuth();

  const [mapState, setMapState] = useState({
    center: RED_SQUARE,
    zoom: 12
  });

  const [selectedProject, setSelectedProject] = useState(null);
  const [userLocation, setUserLocation] = useState(RED_SQUARE);
  const [route, setRoute] = useState(null);
  const [routeLoading, setRouteLoading] = useState(false);
  const [markedProjects, setMarkedProjects] = useState([]);
  const [acceptedDelivery, setAcceptedDelivery] = useState(null);
  const [deliveryStartTime, setDeliveryStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [distanceToDelivery, setDistanceToDelivery] = useState(null);
  const [geolocationWatchId, setGeolocationWatchId] = useState(null);
  const [selectedParcelLocker, setSelectedParcelLocker] = useState(null);
  const [parcelLockers, setParcelLockers] = useState([]);
  const [lockersLoading, setLockersLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const initializeMap = async () => {
      const zoomLocationStr = localStorage.getItem('mapZoomLocation');
      let targetLocation = null;
      
      if (zoomLocationStr) {
        try {
          targetLocation = JSON.parse(zoomLocationStr);
          if (isMounted) {
            setAcceptedDelivery(targetLocation);
            setDeliveryStartTime(new Date());
          }
          localStorage.removeItem('mapZoomLocation');
        } catch (e) {
          console.warn('Invalid mapZoomLocation format:', e);
        }
      }

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const userLoc = [position.coords.latitude, position.coords.longitude];
            if (isMounted) {
              setUserLocation(userLoc);
              
              if (targetLocation) {
                const dist = calculateDistanceBetweenPoints(
                  userLoc[0],
                  userLoc[1],
                  targetLocation.latitude,
                  targetLocation.longitude
                );
                setDistanceToDelivery(dist);
              }
              
              if (targetLocation) {
                setMapState({
                  center: [targetLocation.latitude, targetLocation.longitude],
                  zoom: 16
                });
                console.log('Zooming to delivery location:', [targetLocation.latitude, targetLocation.longitude]);
              } else {
                setMapState({
                  center: userLoc,
                  zoom: 14,
                });
                console.log('User location:', userLoc);
              }
            }
          },
          (error) => {
            console.warn('Geolocation unavailable, using default:', error);
            if (isMounted) {
              setUserLocation(RED_SQUARE);
              if (targetLocation) {
                setMapState({
                  center: [targetLocation.latitude, targetLocation.longitude],
                  zoom: 16,
                });
              }
            }
          }
        );

        const watchId = navigator.geolocation.watchPosition(
          (position) => {
            if (isMounted) {
              const userLoc = [position.coords.latitude, position.coords.longitude];
              setUserLocation(userLoc);
              
              if (targetLocation) {
                const dist = calculateDistanceBetweenPoints(
                  userLoc[0],
                  userLoc[1],
                  targetLocation.latitude,
                  targetLocation.longitude
                );
                setDistanceToDelivery(dist);
              }
            }
          },
          (error) => {
            console.warn('Watch position error:', error);
          },
          {
            enableHighAccuracy: true,
            maximumAge: 0,
            timeout: 5000
          }
        );
        
        if (isMounted) {
          setGeolocationWatchId(watchId);
        }
      } else {
        console.warn('Geolocation not supported');
        if (isMounted) {
          setUserLocation(RED_SQUARE);
          if (targetLocation) {
            setMapState({
              center: [targetLocation.latitude, targetLocation.longitude],
              zoom: 16,
            });
          }
        }
      }
    };

    initializeMap();
    return () => {
      isMounted = false;
      if (geolocationWatchId !== null) {
        navigator.geolocation.clearWatch(geolocationWatchId);
      }
    };
  }, []);

  useEffect(() => {
    const fetchParcelLockers = async () => {
      setLockersLoading(true);
      try {
        const response = await fetch('http://localhost:8000/api/parcel-lockers');
        if (response.ok) {
          const data = await response.json();
          setParcelLockers(data);
        }
      } catch (error) {
        console.error('Error fetching parcel lockers:', error);
      } finally {
        setLockersLoading(false);
      }
    };

    fetchParcelLockers();
  }, []);

  useEffect(() => {
    if (!acceptedDelivery || !deliveryStartTime) return;
    
    const interval = setInterval(() => {
      const now = new Date();
      const elapsed = Math.floor((now - deliveryStartTime) / 1000);
      setElapsedTime(elapsed);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [acceptedDelivery, deliveryStartTime]);

  useEffect(() => {
    if (!acceptedDelivery || distanceToDelivery === null) return;
    
    const distanceInMeters = distanceToDelivery * 1000;
    
    if (distanceInMeters < 10) {
      completeDelivery();
    }
  }, [distanceToDelivery]);

  const calculateDistanceBetweenPoints = (lat1, lon1, lat2, lon2) => {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return (R * c);
  };

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

  const completeDelivery = async () => {
    if (!acceptedDelivery || !deliveryStartTime) return;
    
    try {
      const deliveryTimeMinutes = Math.round(elapsedTime / 60);
      const response = await fetch('http://localhost:5000/api/deliveries/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          delivery_id: acceptedDelivery.deliveryId,
          delivery_time_minutes: deliveryTimeMinutes,
          rating: 5.0
        })
      });
      
      if (response.ok) {
        showToast(`Delivery completed in ${deliveryTimeMinutes} minutes!`, 'success');
        setAcceptedDelivery(null);
        setDeliveryStartTime(null);
        setElapsedTime(0);
        setDistanceToDelivery(null);
      } else {
        showToast('Error completing delivery', 'error');
      }
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m ${secs}s`;
  };


  const buildRoute = async (project) => {
    try {
      setRouteLoading(true);
      
      const locations = [
        {
          id: 'start',
          lat: userLocation[0],
          lon: userLocation[1],
          name: 'Your location',
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
        <h3>Проекты рядом</h3>
        {projectsLoading ? (
          <div className="loading">
            <Loader size={16} className="spinner" />
            Загрузка проектов...
          </div>
        ) : projects.length === 0 ? (
          <div className="empty">Проектов не найдено</div>
        ) : (
          <div className="projects-list">
            {projects.map((project) => {
              const distance = project.latitude && project.longitude 
                ? calculateDistance(
                    mapState.center[0],
                    mapState.center[1],
                    project.latitude,
                    project.longitude
                  )
                : 'N/A';
              return (
                <div
                  key={project.id}
                  className="project-item"
                  onClick={() => {
                    setSelectedProject(project);
                    if (!markedProjects.includes(project.id)) {
                      setMarkedProjects([...markedProjects, project.id]);
                    }
                    if (project.latitude && project.longitude) {
                      setMapState({
                        center: [project.latitude, project.longitude],
                        zoom: 15
                      });
                      buildRoute(project);
                    }
                  }}
                >
                  <div className="project-icon">#{project.id}</div>
                  <div className="project-info">
                    <div className="project-name">{project.name}</div>
                    <div className="project-distance">{distance} {distance !== 'N/A' ? 'км' : ''}</div>
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

          {projects.filter(p => p.latitude && p.longitude).map((project) => (
            <Placemark
              key={project.id}
              geometry={[project.latitude, project.longitude]}
              options={{ 
                preset: 'islands#redIcon',
                iconColor: markedProjects.includes(project.id) || selectedProject?.id === project.id ? '#FF6B35' : '#4ECDC4'
              }}
              properties={{
                balloonContent: `<div><strong>${project.name}</strong></div>`
              }}
            />
          ))}

          {parcelLockers.map((locker) => (
            <Placemark
              key={`locker-${locker.id}`}
              geometry={[locker.latitude, locker.longitude]}
              onClick={() => {
                setSelectedParcelLocker(locker);
                setMapState({
                  center: [locker.latitude, locker.longitude],
                  zoom: 15
                });
              }}
              options={{ 
                preset: 'islands#yellowIcon',
                iconColor: selectedParcelLocker?.id === locker.id ? '#FF6B35' : '#FFB81C'
              }}
              properties={{
                balloonContent: `<div><strong>${locker.name}</strong><br/><small>${locker.address}</small><br/><small>Свободно: ${locker.total_capacity - locker.current_occupancy}/${locker.total_capacity}</small></div>`
              }}
            />
          ))}

          {acceptedDelivery && (
            <Placemark
              geometry={[acceptedDelivery.latitude, acceptedDelivery.longitude]}
              options={{ 
                preset: 'islands#yellowCircleDotIcon',
                iconColor: '#FFD700'
              }}
              properties={{
                balloonContent: `<div><strong>Accepted Delivery</strong><br/>Delivery #${acceptedDelivery.deliveryId}</div>`
              }}
            />
          )}
        </YandexMap>
      </YMaps>

      {acceptedDelivery && (
        <div className="delivery-info-panel">
          <div className="delivery-header">
            <Package size={20} />
            <h3>Активная доставка</h3>
          </div>
          <div className="delivery-details">
            <div className="delivery-detail">
              <Clock size={16} />
              <span className="label">Прошедшее время:</span>
              <span className="value">{formatTime(elapsedTime)}</span>
            </div>
            <div className="delivery-detail">
              <MapPin size={16} />
              <span className="label">Расстояние до места:</span>
              <span className="value">
                {distanceToDelivery !== null 
                  ? `${(distanceToDelivery * 1000).toFixed(0)}м` 
                  : 'Вычисление...'}
              </span>
            </div>
            {distanceToDelivery !== null && distanceToDelivery * 1000 < 50 && (
              <div className="arrival-warning" style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: '#fbbf24', borderRadius: '0.5rem', color: '#000' }}>
                <AlertCircle size={16} style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                Вы близко к месту доставки!
              </div>
            )}
          </div>
        </div>
      )}

      {route && (
        <div className="route-info-panel">
          <div className="route-header">
            <Navigation size={20} />
            <h3>Маршрут до {route.project.name}</h3>
          </div>
          <div className="route-details">
            <div className="route-detail">
              <span className="label">Расстояние:</span>
              <span className="value">{route.distance} км</span>
            </div>
            <div className="route-detail">
              <span className="label">Длительность:</span>
              <span className="value">{route.duration} мин</span>
            </div>
          </div>
          {routeLoading && (
            <div className="route-loading">
              <Loader size={16} className="spinner" />
              Вычисление маршрута...
            </div>
          )}
        </div>
      )}

      {selectedParcelLocker && (
        <div className="parcel-locker-panel">
          <div className="panel-header">
            <Box size={20} />
            <h3>{selectedParcelLocker.name}</h3>
          </div>
          <div className="panel-content">
            <div className="info-row">
              <MapPin size={16} />
              <span>{selectedParcelLocker.address}</span>
            </div>
            <div className="info-row">
              <Package size={16} />
              <span>Свободно ячеек: {selectedParcelLocker.total_capacity - selectedParcelLocker.current_occupancy}/{selectedParcelLocker.total_capacity}</span>
            </div>
            <div className="capacity-bar">
              <div className="capacity-fill" style={{ width: `${((selectedParcelLocker.total_capacity - selectedParcelLocker.current_occupancy) / selectedParcelLocker.total_capacity) * 100}%` }}></div>
            </div>
            <button 
              onClick={() => setSelectedParcelLocker(null)}
              className="close-btn"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapPage;