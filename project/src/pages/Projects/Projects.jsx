import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { projectsAPI, issuesAPI } from '../../services/api';
import { Plus, FileText, Trash2, Edit2, Search, Loader, MapPin, AlertCircle } from 'lucide-react';
import { YMaps } from 'react-yandex-maps';
import './Projects.css';

const YMAPS_API_KEY = '662d65a9-10ee-455d-b361-9f928d10502d';

const MOSCOW_BOUNDS = {
  min_lat: 55.4,
  max_lat: 55.95,
  min_lon: 37.0,
  max_lon: 37.9
};

const isInMoscow = (lat, lon) =>
  lat >= MOSCOW_BOUNDS.min_lat &&
  lat <= MOSCOW_BOUNDS.max_lat &&
  lon >= MOSCOW_BOUNDS.min_lon &&
  lon <= MOSCOW_BOUNDS.max_lon;

const Projects = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [issues, setIssues] = useState([]);
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);
  const [showNewIssueModal, setShowNewIssueModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newProject, setNewProject] = useState({ name: '', description: '', latitude: null, longitude: null });
  const [newIssue, setNewIssue] = useState({ title: '', description: '', priority: 'Medium' });
  
  // Address search states
  const [addressQuery, setAddressQuery] = useState('');
  const [addressResults, setAddressResults] = useState([]);
  const [addressSearching, setAddressSearching] = useState(false);
  const [addressError, setAddressError] = useState('');
  const [selectedAddress, setSelectedAddress] = useState(null);
  
  const ymapsRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchIssues(selectedProject.id);
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await projectsAPI.getAll();
      setProjects(data);
      if (data.length > 0 && !selectedProject) {
        setSelectedProject(data[0]);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIssues = async (projectId) => {
    try {
      const data = await issuesAPI.getByProject(projectId);
      setIssues(data);
    } catch (error) {
      console.error('Error fetching issues:', error);
    }
  };

  // YMaps load handler
  const handleYMapsLoad = (ymaps) => {
    console.log('[YMaps loaded]');
    ymapsRef.current = ymaps;
  };

  // Search address with geocode
  const searchAddress = useCallback(async (q) => {
    if (!q || !q.trim()) {
      setAddressResults([]);
      return;
    }

    if (!ymapsRef.current) return;

    setAddressSearching(true);
    setAddressError('');

    try {
      const hasNumber = /\d+/.test(q);

      const boundedBy = [
        [MOSCOW_BOUNDS.min_lat, MOSCOW_BOUNDS.min_lon],
        [MOSCOW_BOUNDS.max_lat, MOSCOW_BOUNDS.max_lon],
      ];

      const res = await ymapsRef.current.geocode(`Москва, ${q}`, {
        results: 7,
        kind: hasNumber ? 'house' : 'street',
        boundedBy,
        strictBounds: true,
      });

      const list = [];

      res.geoObjects.each((geoObject) => {
        const [lat, lon] = geoObject.geometry.getCoordinates();
        if (!isInMoscow(lat, lon)) return;

        list.push({
          name: geoObject.properties.get('name'),
          address: geoObject.getAddressLine(),
          lat,
          lon
        });
      });

      if (list.length === 0) {
        setAddressError('Адрес не найден в Москве');
      }

      setAddressResults(list);
    } catch (e) {
      console.error(e);
      setAddressError('Ошибка поиска адреса');
    } finally {
      setAddressSearching(false);
    }
  }, []);

  // Handle address input change with debounce
  const handleAddressChange = (value) => {
    setAddressQuery(value);

    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(() => {
      searchAddress(value);
    }, 300);
  };

  // Select address for project
  const selectAddressForProject = (result) => {
    setSelectedAddress(result);
    setNewProject(prev => ({
      ...prev,
      latitude: result.lat,
      longitude: result.lon
    }));
    setAddressQuery('');
    setAddressResults([]);
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    
    if (!newProject.name || !newProject.name.trim()) {
      alert('Пожалуйста, введите название проекта');
      return;
    }
    
    try {
      console.log('[CreateProject] Starting project creation...');
      console.log('[CreateProject] User:', user);
      console.log('[CreateProject] Token in localStorage:', !!localStorage.getItem('authToken'));
      
      const projectData = {
        name: newProject.name,
        description: newProject.description,
        icon: '',
        color: '#6b7280',
        goal_amount: 1000,
        latitude: newProject.latitude,
        longitude: newProject.longitude
      };
      
      console.log('[CreateProject] Sending data:', projectData);
      const created = await projectsAPI.create(projectData);
      
      console.log('[CreateProject] Success! Created project:', created);
      setProjects([...projects, created]);
      setNewProject({ name: '', description: '', latitude: null, longitude: null });
      setSelectedAddress(null);
      setAddressQuery('');
      setShowNewProjectModal(false);
      alert('Проект успешно создан!');
    } catch (error) {
      console.error('[CreateProject] Error:', error);
      console.error('[CreateProject] Error message:', error.message);
      console.error('[CreateProject] Error details:', error);
      
      let errorMessage = error.message || 'Unknown error';
      
      // Check if it's an authentication error
      if (error.message && error.message.includes('Not authenticated')) {
        errorMessage = 'Вы не авторизованы. Пожалуйста, войдите в систему.';
      } else if (error.message && error.message.includes('401')) {
        errorMessage = 'Сессия истекла. Пожалуйста, перезагрузитесь.';
      }
      
      alert('Ошибка при создании проекта:\n' + errorMessage);
    }
  };

  const handleCreateIssue = async (e) => {
    e.preventDefault();
    if (!selectedProject) return;
    
    try {
      const issueData = {
        title: newIssue.title,
        description: newIssue.description,
        project_id: selectedProject.id,
        priority: newIssue.priority
      };
      const created = await issuesAPI.create(issueData);
      setIssues([...issues, created]);
      setNewIssue({ title: '', description: '', priority: 'Medium' });
      setShowNewIssueModal(false);
    } catch (error) {
      console.error('Error creating issue:', error);
      alert('Ошибка при создании задачи: ' + (error.message || 'Unknown error'));
    }
  };

  const handleDeleteProject = async (id) => {
    if (window.confirm('Delete this project?')) {
      try {
        await projectsAPI.delete(id);
        setProjects(projects.filter(p => p.id !== id));
        if (selectedProject?.id === id) {
          setSelectedProject(projects[0] || null);
        }
      } catch (error) {
        console.error('Error deleting project:', error);
      }
    }
  };

  const handleDeleteIssue = async (id) => {
    if (window.confirm('Delete this issue?')) {
      try {
        await issuesAPI.delete(id);
        setIssues(issues.filter(i => i.id !== id));
      } catch (error) {
        console.error('Error deleting issue:', error);
      }
    }
  };

  const handleStatusChange = async (issueId, newStatus) => {
    try {
      const updated = await issuesAPI.updateStatus(issueId, newStatus);
      setIssues(issues.map(i => i.id === issueId ? updated : i));
    } catch (error) {
      console.error('Error updating issue status:', error);
    }
  };

  const statusOptions = ['Backlog', 'Todo', 'In Progress', 'In Review', 'Done'];
  const priorityOptions = ['Low', 'Medium', 'High', 'Urgent'];

  const getStatusColor = (status) => {
    const colors = {
      'Backlog': '#8a8f98',
      'Todo': '#6b7280',
      'In Progress': '#f59e0b',
      'In Review': '#8b5cf6',
      'Done': '#10b981'
    };
    return colors[status] || '#8a8f98';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'Low': '#10b981',
      'Medium': '#6b7280',
      'High': '#f59e0b',
      'Urgent': '#ef4444'
    };
    return colors[priority] || '#8a8f98';
  };

  if (loading) {
    return <div className="projects-container">Loading...</div>;
  }

  return (
    <div className="projects-container">
      <div className="projects-sidebar">
        <div className="projects-header">
          <h2>Projects</h2>
          <button 
            className="btn-icon"
            onClick={() => setShowNewProjectModal(true)}
            title="New project"
          >
            <Plus size={20} />
          </button>
        </div>

        <div className="projects-list">
          {projects.map(project => (
            <div
              key={project.id}
              className={`project-item ${selectedProject?.id === project.id ? 'active' : ''}`}
              onClick={() => setSelectedProject(project)}
            >
              <div className="project-item-left">
                <span className="project-icon">{project.icon}</span>
                <span className="project-name">{project.name}</span>
              </div>
              <button
                className="btn-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteProject(project.id);
                }}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="projects-main">
        {selectedProject ? (
          <>
            <div className="project-header">
              <div>
                <h1>{selectedProject.name}</h1>
                <p className="project-description">{selectedProject.description}</p>
              </div>
              <button 
                className="btn-primary"
                onClick={() => setShowNewIssueModal(true)}
              >
                <Plus size={20} />
                New Issue
              </button>
            </div>

            <div className="issues-board">
              {statusOptions.map(status => (
                <div key={status} className="status-column">
                  <div className="column-header">
                    <span className="status-badge" style={{ borderColor: getStatusColor(status) }}>
                      {status}
                    </span>
                    <span className="issue-count">{issues.filter(i => i.status === status).length}</span>
                  </div>

                  <div className="issues-column">
                    {issues.filter(i => i.status === status).map(issue => (
                      <div key={issue.id} className="issue-card">
                        <div className="issue-header">
                          <h4>{issue.title}</h4>
                          <button
                            className="btn-delete-small"
                            onClick={() => handleDeleteIssue(issue.id)}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>

                        <p className="issue-description">{issue.description}</p>

                        <div className="issue-meta">
                          <select
                            className="status-select"
                            value={issue.status}
                            onChange={(e) => handleStatusChange(issue.id, e.target.value)}
                          >
                            {statusOptions.map(s => (
                              <option key={s} value={s}>{s}</option>
                            ))}
                          </select>

                          <span 
                            className="priority-badge"
                            style={{ backgroundColor: getPriorityColor(issue.priority) }}
                          >
                            {issue.priority}
                          </span>
                        </div>

                        {issue.dueDate && (
                          <div className="issue-due-date">
                            Due: {new Date(issue.dueDate).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="no-project">
            <FileText size={48} />
            <p>No projects yet. Create one to get started!</p>
          </div>
        )}
      </div>

      {/* New Project Modal */}
      {showNewProjectModal && (
        <div className="modal-overlay" onClick={() => setShowNewProjectModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Project</h2>
            <YMaps
              query={{ apikey: YMAPS_API_KEY, lang: 'ru_RU' }}
              onLoad={handleYMapsLoad}
            >
              <form onSubmit={handleCreateProject}>
                <div className="form-group">
                  <label>Project Name</label>
                  <input
                    type="text"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    placeholder="Enter project name"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    placeholder="Enter project description"
                  />
                </div>

                {/* Address Search */}
                <div className="form-group">
                  <label>Project Location (Moscow)</label>
                  <div className="address-search-wrapper">
                    <Search size={16} className="search-icon" />
                    <input
                      type="text"
                      value={addressQuery}
                      onChange={(e) => handleAddressChange(e.target.value)}
                      placeholder="Search street or address..."
                      className="address-input"
                    />
                    {addressSearching && <Loader size={16} className="spinner" />}
                  </div>

                  {addressError && (
                    <div className="error-message-small">
                      <AlertCircle size={14} />
                      {addressError}
                    </div>
                  )}

                  {addressResults.length > 0 && (
                    <div className="address-results">
                      {addressResults.map((result, idx) => (
                        <div
                          key={idx}
                          className="address-result-item"
                          onClick={() => selectAddressForProject(result)}
                        >
                          <MapPin size={14} />
                          <div>
                            <div className="result-name">{result.name}</div>
                            <div className="result-address">{result.address}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {selectedAddress && (
                    <div className="selected-address">
                      <MapPin size={16} />
                      <div>
                        <div className="selected-name">{selectedAddress.name}</div>
                        <div className="selected-coords">
                          {selectedAddress.lat.toFixed(4)}, {selectedAddress.lon.toFixed(4)}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="modal-buttons">
                  <button 
                    type="button" 
                    className="btn-cancel" 
                    onClick={() => {
                      setShowNewProjectModal(false);
                      setAddressQuery('');
                      setAddressResults([]);
                      setSelectedAddress(null);
                    }}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">Create</button>
                </div>
              </form>
            </YMaps>
          </div>
        </div>
      )}

      {/* New Issue Modal */}
      {showNewIssueModal && (
        <div className="modal-overlay" onClick={() => setShowNewIssueModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Issue</h2>
            <form onSubmit={handleCreateIssue}>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={newIssue.title}
                  onChange={(e) => setNewIssue({ ...newIssue, title: e.target.value })}
                  placeholder="Enter issue title"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newIssue.description}
                  onChange={(e) => setNewIssue({ ...newIssue, description: e.target.value })}
                  placeholder="Enter issue description"
                />
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  value={newIssue.priority}
                  onChange={(e) => setNewIssue({ ...newIssue, priority: e.target.value })}
                >
                  {priorityOptions.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div className="modal-buttons">
                <button type="button" className="btn-cancel" onClick={() => setShowNewIssueModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Projects;
