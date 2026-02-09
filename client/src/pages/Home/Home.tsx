import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchProjects } from '../../store/slices/projectSlice'
import { AppDispatch, RootState } from '../../store/store'
import ProjectHealthBadge from '../../components/ProjectStatus/ProjectHealthBadge'
import './Home.css'

const Home: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { projects, loading } = useSelector((state: RootState) => state.projects)

  useEffect(() => {
    dispatch(fetchProjects({ limit: 12 }))
  }, [dispatch])

  return (
    <div className="home">
      <div className="home-header">
        <h2>Welcome to Project Status Tracker</h2>
        <p>This application allows tech leads to update project status through AI-powered transcription processing.</p>
      </div>

      <div className="home-projects-section">
        <div className="home-projects-header">
          <h3>Recent Projects</h3>
          <button onClick={() => navigate('/projects')} className="btn-view-all">
            View All Projects
          </button>
        </div>

        {loading && projects.length === 0 ? (
          <div className="loading-state">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="empty-state">
            <p>No projects found.</p>
            <button onClick={() => navigate('/projects/new')} className="btn-primary">
              Create Your First Project
            </button>
          </div>
        ) : (
          <div className="projects-grid-square">
            {projects.map((project) => (
              <div
                key={project.id}
                className="project-card-square"
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                <div className="project-card-square-header">
                  <div className="project-card-title-row">
                    <h4>{project.name}</h4>
                    <ProjectHealthBadge projectId={project.id} />
                  </div>
                </div>
                <div className="project-card-square-body">
                  <p className="project-client">{project.client?.name || 'N/A'}</p>
                  <p className="project-date">
                    {new Date(project.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Home
