import React, { useEffect, useState } from 'react'
import api from '../../services/api'
import {
  calculateProjectHealthStatus,
  getHealthStatusLabel,
  ProjectStatusFields
} from '../../utils/projectStatusUtils'
import './ProjectHealthBadge.css'

interface ProjectHealthBadgeProps {
  projectId: number
}

const ProjectHealthBadge: React.FC<ProjectHealthBadgeProps> = ({ projectId }) => {
  const [status, setStatus] = useState<ProjectStatusFields | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    const fetchStatus = async () => {
      try {
        setLoading(true)
        const response = await api.get(`/project-status/project/${projectId}/latest`)
        if (isMounted) {
          setStatus(response.data)
        }
      } catch (error: any) {
        // 404 means no status exists, which is fine
        if (error.response?.status !== 404 && isMounted) {
          console.error(`Failed to fetch status for project ${projectId}:`, error)
        }
        if (isMounted) {
          setStatus(null)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchStatus()

    return () => {
      isMounted = false
    }
  }, [projectId])

  if (loading) {
    return <span className="health-badge-loading">...</span>
  }

  if (!status) {
    return <span className="health-badge health-red" title="No status available">—</span>
  }

  const healthStatus = calculateProjectHealthStatus(status)
  const healthLabel = getHealthStatusLabel(healthStatus)

  return (
    <span
      className={`health-badge health-${healthStatus}`}
      title={`Project Health: ${healthLabel}`}
    >
      {healthLabel}
    </span>
  )
}

export default ProjectHealthBadge
