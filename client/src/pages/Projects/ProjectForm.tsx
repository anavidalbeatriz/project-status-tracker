import React, { useState, FormEvent, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { createProject, updateProject, fetchProject, clearError, clearCurrentProject } from '../../store/slices/projectSlice'
import { fetchClients } from '../../store/slices/clientSlice'
import { AppDispatch, RootState } from '../../store/store'
import './ProjectForm.css'

const ProjectForm: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  const { currentProject, loading, error } = useSelector((state: RootState) => state.projects)
  const { clients, loading: clientsLoading } = useSelector((state: RootState) => state.clients)

  const [name, setName] = useState('')
  const [clientId, setClientId] = useState<number | ''>('')

  useEffect(() => {
    dispatch(fetchClients())
    if (isEdit && id) {
      dispatch(fetchProject(parseInt(id)))
    }
    return () => {
      dispatch(clearCurrentProject())
      dispatch(clearError())
    }
  }, [id, isEdit, dispatch])

  // Refresh clients list when component becomes visible (e.g., returning from client creation)
  useEffect(() => {
    const handleFocus = () => {
      dispatch(fetchClients())
    }
    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [dispatch])

  useEffect(() => {
    if (isEdit && currentProject) {
      setName(currentProject.name)
      setClientId(currentProject.client_id)
    }
  }, [isEdit, currentProject])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    dispatch(clearError())

    if (!clientId) {
      return
    }

    try {
      if (isEdit && id) {
        await dispatch(updateProject({ id: parseInt(id), data: { name, client_id: Number(clientId) } })).unwrap()
      } else {
        await dispatch(createProject({ name, client_id: Number(clientId) })).unwrap()
      }
      navigate('/projects')
    } catch (err) {
      // Error is handled by Redux
    }
  }

  if (isEdit && loading && !currentProject) {
    return <div className="project-form-container">Loading...</div>
  }

  return (
    <div className="project-form-container">
      <div className="project-form-header">
        <h2>{isEdit ? 'Edit Project' : 'Create New Project'}</h2>
        <button onClick={() => navigate('/projects')} className="btn-back">
          ← Back to Projects
        </button>
      </div>

      <div className="project-form-card">
        {error && (
          <div className="error-message" onClick={() => dispatch(clearError())}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Project Name *</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={loading}
              placeholder="Enter project name"
            />
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label htmlFor="client">Client *</label>
              <button
                type="button"
                onClick={() => {
                  navigate('/clients/new?from=project')
                }}
                className="btn-link"
                style={{ fontSize: '0.9rem', padding: '0.25rem 0.5rem' }}
              >
                + Create New Client
              </button>
            </div>
            <select
              id="client"
              value={clientId}
              onChange={(e) => setClientId(e.target.value ? Number(e.target.value) : '')}
              required
              disabled={loading || clientsLoading}
            >
              <option value="">Select a client</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="button" onClick={() => navigate('/projects')} className="btn-cancel" disabled={loading}>
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Saving...' : isEdit ? 'Update Project' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProjectForm
