import React, { useState, useEffect } from 'react';
import './SimpleMapPage.css';
import { MapPin, Package, AlertCircle } from 'lucide-react';
import { YMaps, Map as YandexMap, Placemark, ZoomControl, FullscreenControl } from 'react-yandex-maps';
import { projectsAPI } from '../../services/api';

const RED_SQUARE = [55.7536, 37.6201];

const SimpleMapPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedProject, setSelectedProject] = useState(null);
  const [mapState, setMapState] = useState({
    center: RED_SQUARE,
    zoom: 12,
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError('');
      console.log('[SimpleMap] Fetching projects from API...');
      const data = await projectsAPI.getAll();
      console.log('[SimpleMap] Projects received:', data);
      
      if (!Array.isArray(data)) {
        throw new Error('Invalid data format from API');
      }
      
      const validProjects = data.filter(p => p.latitude && p.longitude);
      console.log(`[SimpleMap] Found ${data.length} projects, ${validProjects.length} have location data`);
      setProjects(validProjects);
      
      if (validProjects.length === 0 && data.length > 0) {
        setError(`Found ${data.length} projects, but they don't have location data`);
      }
    } catch (err) {
      console.error('[SimpleMap] Error fetching projects:', err);
      const errorMessage = err.message || 'Failed to load projects';
      setError(`Error loading: ${errorMessage}`);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    if (project.latitude && project.longitude) {
      setMapState({
        center: [project.latitude, project.longitude],
        zoom: 15,
      });
    }
  };

  const getPlacemarkColor = (index) => {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'];
    return colors[index % colors.length];
  };

  const renderPlacemarks = () => {
    return projects.map((project, index) => (
      <Placemark
        key={project.id}
        defaultGeometry={[project.latitude, project.longitude]}
        defaultProperties={{
          name: project.name,
          description: `${project.description || 'No description'}`
        }}
        options={{
          preset: 'islands#redIcon',
          iconColor: getPlacemarkColor(index)
        }}
        onClick={() => handleProjectSelect(project)}
      />
    ));
  };

  if (loading) {
    return (
      <div className="simple-map-container">
        <div className="map-loading">
          <div className="spinner"></div>
          <p>Loading map...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="simple-map-container">
      <div className="simple-map-wrapper">
        <YMaps>
          <div className="simple-map-content">
            <YandexMap
              state={mapState}
              width="100%"
              height="100%"
              options={{
                minZoom: 2,
                maxZoom: 21,
                suppressMapOpenBlock: true
              }}
            >
              <ZoomControl options={{ position: { right: 10, top: 10 } }} />
              <FullscreenControl options={{ position: { right: 10, bottom: 10 } }} />
              {renderPlacemarks()}
            </YandexMap>
          </div>
        </YMaps>
      </div>

      <div className="simple-map-sidebar">
        <div className="simple-sidebar-header">
          <MapPin size={24} />
          <h2>All Projects</h2>
        </div>

        {error && (
          <div className="simple-error-message">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {projects.length === 0 ? (
          <div className="simple-no-projects">
            <Package size={32} />
            <p>No projects with location data</p>
          </div>
        ) : (
          <div className="simple-projects-list">
            {projects.map((project, index) => (
              <div
                key={project.id}
                className={`simple-project-item ${selectedProject?.id === project.id ? 'selected' : ''}`}
                onClick={() => handleProjectSelect(project)}
              >
                <div 
                  className="simple-project-marker" 
                  style={{ backgroundColor: getPlacemarkColor(index) }}
                ></div>
                <div className="simple-project-info">
                  <h3>{project.name}</h3>
                  <p className="simple-project-location">
                    {project.latitude.toFixed(4)}, {project.longitude.toFixed(4)}
                  </p>
                  {project.description && (
                    <p className="simple-project-description">{project.description}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="simple-sidebar-footer">
          <p className="simple-project-count">
            Total projects: <strong>{projects.length}</strong>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimpleMapPage;
