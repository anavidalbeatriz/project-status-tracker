import React, { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { fetchProject, clearCurrentProject } from '../../store/slices/projectSlice'
import { fetchTranscriptions, deleteTranscription, clearError as clearTranscriptionError } from '../../store/slices/transcriptionSlice'
import { fetchLatestProjectStatus } from '../../store/slices/projectStatusSlice'
import { AppDispatch, RootState } from '../../store/store'
import TranscriptionUpload from '../../components/TranscriptionUpload/TranscriptionUpload'
import ProjectStatusDisplay from '../../components/ProjectStatus/ProjectStatusDisplay'
import './ProjectDetail.css'

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  const { currentProject, loading, error } = useSelector((state: RootState) => state.projects)
  const { transcriptions, loading: transcriptionsLoading } = useSelector((state: RootState) => state.transcriptions)

  useEffect(() => {
    if (id) {
      const projectId = parseInt(id)
      dispatch(fetchProject(projectId))
      dispatch(fetchTranscriptions(projectId))
      dispatch(fetchLatestProjectStatus(projectId))
    }
    return () => {
      dispatch(clearCurrentProject())
      dispatch(clearTranscriptionError())
    }
  }, [id, dispatch])

  const handleUploadSuccess = () => {
    if (id) {
      const projectId = parseInt(id)
      dispatch(fetchTranscriptions(projectId))
      // Refresh status after a short delay to allow AI processing
      setTimeout(() => {
        dispatch(fetchLatestProjectStatus(projectId))
      }, 3000)
    }
  }

  const handleDeleteTranscription = async (transcriptionId: number) => {
    if (!window.confirm('Are you sure you want to delete this transcription?')) {
      return
    }

    try {
      await dispatch(deleteTranscription(transcriptionId)).unwrap()
      if (id) {
        dispatch(fetchTranscriptions(parseInt(id)))
      }
    } catch (err) {
      // Error is handled by Redux
    }
  }

  if (loading) {
    return <div className="project-detail-container">Loading...</div>
  }

  if (error || !currentProject) {
    return (
      <div className="project-detail-container">
        <div className="error-message">{error || 'Project not found'}</div>
        <button onClick={() => navigate('/projects')} className="btn-primary">
          Back to Projects
        </button>
      </div>
    )
  }

  return (
    <div className="project-detail-container">
      <div className="project-detail-header">
        <button onClick={() => navigate('/projects')} className="btn-back">
          ← Back to Projects
        </button>
        <div className="project-detail-actions">
          <button
            onClick={() => navigate(`/projects/${id}/edit`)}
            className="btn-edit"
          >
            Edit
          </button>
        </div>
      </div>

      <div className="project-detail-card">
        <h1>{currentProject.name}</h1>
        <div className="project-detail-info">
          <div className="info-row">
            <strong>Client:</strong>
            <span>{currentProject.client?.name || 'N/A'}</span>
          </div>
          {currentProject.creator && (
            <div className="info-row">
              <strong>Created by:</strong>
              <span>{currentProject.creator.name} ({currentProject.creator.email})</span>
            </div>
          )}
          <div className="info-row">
            <strong>Created:</strong>
            <span>{new Date(currentProject.created_at).toLocaleString()}</span>
          </div>
          {currentProject.updated_at && (
            <div className="info-row">
              <strong>Last updated:</strong>
              <span>{new Date(currentProject.updated_at).toLocaleString()}</span>
            </div>
          )}
        </div>
      </div>

      <div className="transcriptions-section">
        <h2>Transcriptions</h2>
        <TranscriptionUpload projectId={currentProject.id} onUploadSuccess={handleUploadSuccess} />
        
        {transcriptionsLoading ? (
          <p>Loading transcriptions...</p>
        ) : transcriptions.length === 0 ? (
          <p className="no-transcriptions">No transcriptions uploaded yet.</p>
        ) : (
          <div className="transcriptions-list">
            {transcriptions.map((transcription) => (
              <div key={transcription.id} className="transcription-item">
                <div className="transcription-info">
                  <h4>{transcription.file_name || 'Untitled'}</h4>
                  <div className="transcription-meta">
                    <span className="file-type">{transcription.file_type || 'unknown'}</span>
                    {transcription.file_size && (
                      <span className="file-size">
                        {(transcription.file_size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    )}
                    <span className="upload-date">
                      {new Date(transcription.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {transcription.processed_at && (
                    <p className="processed-badge">Processed</p>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteTranscription(transcription.id)}
                  className="btn-delete-transcription"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {currentProject && (
        <ProjectStatusDisplay projectId={currentProject.id} />
      )}
    </div>
  )
}

export default ProjectDetail
