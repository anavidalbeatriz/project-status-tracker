import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../../store/store'
import {
  fetchLatestProjectStatus,
  updateProjectStatus,
  createProjectStatus,
  ProjectStatusUpdate
} from '../../store/slices/projectStatusSlice'
import {
  calculateProjectHealthStatus,
  getHealthStatusLabel,
  getHealthStatusDescription
} from '../../utils/projectStatusUtils'
import './ProjectStatusDisplay.css'

interface ProjectStatusDisplayProps {
  projectId: number
}

const ProjectStatusDisplay: React.FC<ProjectStatusDisplayProps> = ({ projectId }) => {
  const dispatch = useDispatch<AppDispatch>()
  const { latestStatus, loading, error } = useSelector((state: RootState) => state.projectStatus)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<ProjectStatusUpdate>({
    is_on_scope: null,
    is_on_time: null,
    is_on_budget: null,
    next_delivery: null,
    risks: null
  })

  React.useEffect(() => {
    dispatch(fetchLatestProjectStatus(projectId))
  }, [dispatch, projectId])

  React.useEffect(() => {
    if (latestStatus) {
      setFormData({
        is_on_scope: latestStatus.is_on_scope,
        is_on_time: latestStatus.is_on_time,
        is_on_budget: latestStatus.is_on_budget,
        next_delivery: latestStatus.next_delivery,
        risks: latestStatus.risks
      })
    }
  }, [latestStatus])

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleCancel = () => {
    setIsEditing(false)
    if (latestStatus) {
      setFormData({
        is_on_scope: latestStatus.is_on_scope,
        is_on_time: latestStatus.is_on_time,
        is_on_budget: latestStatus.is_on_budget,
        next_delivery: latestStatus.next_delivery,
        risks: latestStatus.risks
      })
    }
  }

  const handleSave = async () => {
    try {
      if (latestStatus) {
        await dispatch(updateProjectStatus({ statusId: latestStatus.id, statusData: formData })).unwrap()
      } else {
        await dispatch(createProjectStatus({ project_id: projectId, ...formData })).unwrap()
      }
      setIsEditing(false)
      dispatch(fetchLatestProjectStatus(projectId))
    } catch (err) {
      // Error is handled by Redux
    }
  }

  const handleBooleanChange = (field: 'is_on_scope' | 'is_on_time' | 'is_on_budget', value: boolean | null) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleTextChange = (field: 'next_delivery' | 'risks', value: string) => {
    setFormData(prev => ({ ...prev, [field]: value || null }))
  }

  const getStatusBadge = (value: boolean | null) => {
    if (value === true) return <span className="status-badge status-yes">Yes</span>
    if (value === false) return <span className="status-badge status-no">No</span>
    return <span className="status-badge status-unknown">Unknown</span>
  }

  const getStatusSelect = (field: 'is_on_scope' | 'is_on_time' | 'is_on_budget', value: boolean | null) => {
    return (
      <select
        value={value === null ? 'null' : value.toString()}
        onChange={(e) => {
          const val = e.target.value === 'null' ? null : e.target.value === 'true'
          handleBooleanChange(field, val)
        }}
        className="status-select"
      >
        <option value="null">Unknown</option>
        <option value="true">Yes</option>
        <option value="false">No</option>
      </select>
    )
  }

  if (loading && !latestStatus) {
    return <div className="project-status-container">Loading status...</div>
  }

  const healthStatus = calculateProjectHealthStatus(latestStatus)
  const healthLabel = getHealthStatusLabel(healthStatus)
  const healthDescription = getHealthStatusDescription(healthStatus)

  return (
    <div className="project-status-container">
      <div className="project-status-header">
        <div>
          <h2>Project Status</h2>
          {latestStatus && (
            <div className="health-indicator">
              <span className={`health-flag health-${healthStatus}`} title={healthDescription}>
                {healthLabel}
              </span>
            </div>
          )}
        </div>
        {!isEditing && (
          <button onClick={handleEdit} className="btn-edit-status">
            {latestStatus ? 'Edit' : 'Create Status'}
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {!latestStatus && !isEditing ? (
        <div className="no-status">
          <p>No status information available yet.</p>
          <p className="hint">Upload a transcription file to automatically extract status, or create one manually.</p>
        </div>
      ) : (
        <div className="status-form">
          <div className="status-field">
            <label>
              <strong>On Scope:</strong>
            </label>
            {isEditing ? (
              getStatusSelect('is_on_scope', formData.is_on_scope ?? null)
            ) : (
              getStatusBadge(latestStatus?.is_on_scope ?? null)
            )}
          </div>

          <div className="status-field">
            <label>
              <strong>On Time:</strong>
            </label>
            {isEditing ? (
              getStatusSelect('is_on_time', formData.is_on_time ?? null)
            ) : (
              getStatusBadge(latestStatus?.is_on_time ?? null)
            )}
          </div>

          <div className="status-field">
            <label>
              <strong>On Budget:</strong>
            </label>
            {isEditing ? (
              getStatusSelect('is_on_budget', formData.is_on_budget ?? null)
            ) : (
              getStatusBadge(latestStatus?.is_on_budget ?? null)
            )}
          </div>

          <div className="status-field">
            <label>
              <strong>Next Delivery:</strong>
            </label>
            {isEditing ? (
              <textarea
                value={formData.next_delivery || ''}
                onChange={(e) => handleTextChange('next_delivery', e.target.value)}
                className="status-textarea"
                placeholder="Enter next delivery information..."
                rows={3}
              />
            ) : (
              <div className="status-text">{latestStatus?.next_delivery || 'Not specified'}</div>
            )}
          </div>

          <div className="status-field">
            <label>
              <strong>Risks:</strong>
            </label>
            {isEditing ? (
              <textarea
                value={formData.risks || ''}
                onChange={(e) => handleTextChange('risks', e.target.value)}
                className="status-textarea"
                placeholder="Enter project risks..."
                rows={4}
              />
            ) : (
              <div className="status-text">{latestStatus?.risks || 'No risks identified'}</div>
            )}
          </div>

          {latestStatus && (
            <div className="status-meta">
              <small>
                Last updated: {new Date(latestStatus.updated_at).toLocaleString()}
                {latestStatus.updater && ` by ${latestStatus.updater.name}`}
              </small>
            </div>
          )}

          {isEditing && (
            <div className="status-actions">
              <button onClick={handleSave} className="btn-save" disabled={loading}>
                {loading ? 'Saving...' : 'Save'}
              </button>
              <button onClick={handleCancel} className="btn-cancel" disabled={loading}>
                Cancel
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ProjectStatusDisplay
