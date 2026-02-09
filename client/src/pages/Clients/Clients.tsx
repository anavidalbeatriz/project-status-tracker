import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchClients, clearError } from '../../store/slices/clientSlice'
import { AppDispatch, RootState } from '../../store/store'
import './Clients.css'

const Clients: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { clients, loading, error } = useSelector((state: RootState) => state.clients)

  useEffect(() => {
    dispatch(fetchClients())
  }, [dispatch])

  if (loading && clients.length === 0) {
    return <div className="clients-container">Loading...</div>
  }

  return (
    <div className="clients-container">
      <div className="clients-header">
        <h2>Clients</h2>
        <button onClick={() => navigate('/clients/new')} className="btn-primary">
          Create New Client
        </button>
      </div>

      {error && (
        <div className="error-message" onClick={() => dispatch(clearError())}>
          {error}
        </div>
      )}

      {clients.length === 0 ? (
        <div className="empty-state">
          <p>No clients found.</p>
          <button onClick={() => navigate('/clients/new')} className="btn-primary">
            Create Your First Client
          </button>
        </div>
      ) : (
        <div className="clients-grid">
          {clients.map((client) => (
            <div key={client.id} className="client-card">
              <div className="client-card-header">
                <h3>{client.name}</h3>
              </div>
              <div className="client-card-body">
                <p><strong>Created:</strong> {new Date(client.created_at).toLocaleDateString()}</p>
                {client.updated_at && (
                  <p><strong>Updated:</strong> {new Date(client.updated_at).toLocaleDateString()}</p>
                )}
                
                {client.projects && client.projects.length > 0 ? (
                  <div className="client-projects">
                    <p className="projects-label"><strong>Projects ({client.projects.length}):</strong></p>
                    <ul className="projects-list">
                      {client.projects.map((project) => (
                        <li 
                          key={project.id} 
                          className="project-item"
                          onClick={() => navigate(`/projects/${project.id}`)}
                        >
                          {project.name}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="client-projects">
                    <p className="no-projects">No projects yet</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Clients
