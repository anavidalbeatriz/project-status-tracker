import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchProjects, deleteProject, clearError } from '../../store/slices/projectSlice'
import { AppDispatch, RootState } from '../../store/store'
import ProjectHealthBadge from '../../components/ProjectStatus/ProjectHealthBadge'
import './Projects.css'

const Projects: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { projects, loading, error } = useSelector((state: RootState) => state.projects)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    dispatch(fetchProjects({}))
  }, [dispatch])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    dispatch(fetchProjects({ search: searchTerm }))
  }

  const handleDelete = async (projectId: number, projectName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${projectName}"?`)) {
      return
    }

    try {
      await dispatch(deleteProject(projectId)).unwrap()
      dispatch(fetchProjects({}))
    } catch (err) {
      // Error is handled by Redux
    }
  }

  if (loading && projects.length === 0) {
    return <div className="projects-container">Loading...</div>
  }

  return (
    <div className="projects-container">
      <div className="projects-header">
        <h2>Projects</h2>
        <button onClick={() => navigate('/projects/new')} className="btn-primary">
          Create New Project
        </button>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Search projects by name or client..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <button type="submit" className="btn-search">Search</button>
        {searchTerm && (
          <button
            type="button"
            onClick={() => {
              setSearchTerm('')
              dispatch(fetchProjects({}))
            }}
            className="btn-clear"
          >
            Clear
          </button>
        )}
      </form>

      {error && (
        <div className="error-message" onClick={() => dispatch(clearError())}>
          {error}
        </div>
      )}

      {projects.length === 0 ? (
        <div className="empty-state">
          <p>No projects found.</p>
          <button onClick={() => navigate('/projects/new')} className="btn-primary">
            Create Your First Project
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.id} className="project-card">
              <div className="project-card-header">
                <div className="project-card-title-row">
                  <h3>{project.name}</h3>
                  <ProjectHealthBadge projectId={project.id} />
                </div>
                <div className="project-actions">
                  <button
                    onClick={() => navigate(`/projects/${project.id}`)}
                    className="btn-view"
                  >
                    View
                  </button>
                  <button
                    onClick={() => navigate(`/projects/${project.id}/edit`)}
                    className="btn-edit"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(project.id, project.name)}
                    className="btn-delete"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="project-card-body">
                <p><strong>Client:</strong> {project.client?.name || 'N/A'}</p>
                <p><strong>Created:</strong> {new Date(project.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Projects
