import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../../store/store'
import { generateReport, ReportFilters } from '../../store/slices/reportSlice'
import { fetchClients } from '../../store/slices/clientSlice'
import './Reports.css'

const Reports: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { report, loading, error } = useSelector((state: RootState) => state.report)
  const { clients } = useSelector((state: RootState) => state.clients)
  const [filters, setFilters] = useState<ReportFilters>({
    include_no_status: true
  })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    dispatch(fetchClients())
    dispatch(generateReport())
  }, [dispatch])

  const handleGenerateReport = () => {
    dispatch(generateReport(filters))
  }

  const handleFilterChange = (key: keyof ReportFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleClientToggle = (clientId: number) => {
    const currentIds = filters.client_ids || []
    const newIds = currentIds.includes(clientId)
      ? currentIds.filter(id => id !== clientId)
      : [...currentIds, clientId]
    handleFilterChange('client_ids', newIds.length > 0 ? newIds : undefined)
  }

  const exportToCSV = () => {
    if (!report) return

    const csvRows = []
    
    // Overall metrics
    csvRows.push('Overall Health Metrics')
    csvRows.push(`Total Projects,${report.overall_metrics.total_projects}`)
    csvRows.push(`Healthy Projects,${report.overall_metrics.healthy_projects}`)
    csvRows.push(`At Risk Projects,${report.overall_metrics.at_risk_projects}`)
    csvRows.push(`Critical Projects,${report.overall_metrics.critical_projects}`)
    csvRows.push(`Overall Health %,${report.overall_metrics.overall_health_percentage}%`)
    csvRows.push(`Scope Compliance %,${report.overall_metrics.scope_compliance}%`)
    csvRows.push(`Time Compliance %,${report.overall_metrics.time_compliance}%`)
    csvRows.push(`Budget Compliance %,${report.overall_metrics.budget_compliance}%`)
    csvRows.push('')
    
    // Project metrics
    csvRows.push('Project Metrics')
    csvRows.push('Project Name,Client,Health Status,On Scope,On Time,On Budget,Next Delivery,Risks')
    report.project_metrics.forEach(project => {
      csvRows.push([
        project.project_name,
        project.client_name,
        project.health_label,
        project.is_on_scope === null ? 'Unknown' : project.is_on_scope ? 'Yes' : 'No',
        project.is_on_time === null ? 'Unknown' : project.is_on_time ? 'Yes' : 'No',
        project.is_on_budget === null ? 'Unknown' : project.is_on_budget ? 'Yes' : 'No',
        project.next_delivery || 'N/A',
        (project.risks || 'N/A').replace(/,/g, ';')
      ].join(','))
    })

    const csvContent = csvRows.join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `project-health-report-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="reports-container">
      <div className="reports-header">
        <h2>Project Health Report</h2>
        <div className="reports-actions">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-filter"
          >
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </button>
          <button
            onClick={handleGenerateReport}
            className="btn-generate"
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Report'}
          </button>
          {report && (
            <button
              onClick={exportToCSV}
              className="btn-export"
            >
              Export CSV
            </button>
          )}
        </div>
      </div>

      {showFilters && (
        <div className="report-filters">
          <h3>Filters</h3>
          <div className="filter-group">
            <label>Health Status:</label>
            <select
              value={filters.health_status || ''}
              onChange={(e) => handleFilterChange('health_status', e.target.value || undefined)}
            >
              <option value="">All</option>
              <option value="green">Healthy</option>
              <option value="yellow">At Risk</option>
              <option value="red">Critical</option>
              <option value="none">No Status</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Clients:</label>
            <div className="client-checkboxes">
              {clients.map(client => (
                <label key={client.id} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.client_ids?.includes(client.id) || false}
                    onChange={() => handleClientToggle(client.id)}
                  />
                  {client.name}
                </label>
              ))}
            </div>
          </div>
          <div className="filter-group">
            <label>
              <input
                type="checkbox"
                checked={filters.include_no_status !== false}
                onChange={(e) => handleFilterChange('include_no_status', e.target.checked)}
              />
              Include projects with no status
            </label>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">{error}</div>
      )}

      {loading && !report ? (
        <div className="loading-state">Generating report...</div>
      ) : report ? (
        <div className="report-content">
          {/* Overall Metrics */}
          <div className="metrics-section">
            <h3>Overall Health Metrics</h3>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{report.overall_metrics.total_projects}</div>
                <div className="metric-label">Total Projects</div>
              </div>
              <div className="metric-card healthy">
                <div className="metric-value">{report.overall_metrics.healthy_projects}</div>
                <div className="metric-label">Healthy</div>
                <div className="metric-percentage">
                  {((report.overall_metrics.healthy_projects / report.overall_metrics.total_projects) * 100).toFixed(1)}%
                </div>
              </div>
              <div className="metric-card at-risk">
                <div className="metric-value">{report.overall_metrics.at_risk_projects}</div>
                <div className="metric-label">At Risk</div>
                <div className="metric-percentage">
                  {((report.overall_metrics.at_risk_projects / report.overall_metrics.total_projects) * 100).toFixed(1)}%
                </div>
              </div>
              <div className="metric-card critical">
                <div className="metric-value">{report.overall_metrics.critical_projects}</div>
                <div className="metric-label">Critical</div>
                <div className="metric-percentage">
                  {((report.overall_metrics.critical_projects / report.overall_metrics.total_projects) * 100).toFixed(1)}%
                </div>
              </div>
            </div>
            <div className="compliance-metrics">
              <h4>Compliance Metrics</h4>
              <div className="compliance-bars">
                <div className="compliance-item">
                  <label>Scope Compliance</label>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${report.overall_metrics.scope_compliance}%` }}
                    />
                    <span className="progress-text">{report.overall_metrics.scope_compliance}%</span>
                  </div>
                </div>
                <div className="compliance-item">
                  <label>Time Compliance</label>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${report.overall_metrics.time_compliance}%` }}
                    />
                    <span className="progress-text">{report.overall_metrics.time_compliance}%</span>
                  </div>
                </div>
                <div className="compliance-item">
                  <label>Budget Compliance</label>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${report.overall_metrics.budget_compliance}%` }}
                    />
                    <span className="progress-text">{report.overall_metrics.budget_compliance}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Client Summaries */}
          {report.client_summaries.length > 0 && (
            <div className="section">
              <h3>Client Health Summary</h3>
              <div className="client-summaries-table">
                <table>
                  <thead>
                    <tr>
                      <th>Client</th>
                      <th>Total Projects</th>
                      <th>Healthy</th>
                      <th>At Risk</th>
                      <th>Critical</th>
                      <th>Health %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.client_summaries.map(client => (
                      <tr key={client.client_id}>
                        <td>{client.client_name}</td>
                        <td>{client.total_projects}</td>
                        <td className="healthy-cell">{client.healthy_projects}</td>
                        <td className="at-risk-cell">{client.at_risk_projects}</td>
                        <td className="critical-cell">{client.critical_projects}</td>
                        <td>
                          <div className="health-percentage-bar">
                            <div
                              className="health-percentage-fill"
                              style={{ width: `${client.health_percentage}%` }}
                            />
                            <span>{client.health_percentage}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Projects at Risk */}
          {report.projects_at_risk.length > 0 && (
            <div className="section">
              <h3>Projects at Risk ({report.projects_at_risk.length})</h3>
              <div className="projects-list">
                {report.projects_at_risk.map(project => (
                  <div key={project.project_id} className="project-item at-risk">
                    <div className="project-item-header">
                      <strong>{project.project_name}</strong>
                      <span className="health-badge health-yellow">{project.health_label}</span>
                    </div>
                    <div className="project-item-details">
                      <span>Client: {project.client_name}</span>
                      {project.next_delivery && (
                        <span>Next Delivery: {project.next_delivery}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Critical Projects */}
          {report.critical_projects.length > 0 && (
            <div className="section">
              <h3>Critical Projects ({report.critical_projects.length})</h3>
              <div className="projects-list">
                {report.critical_projects.map(project => (
                  <div key={project.project_id} className="project-item critical">
                    <div className="project-item-header">
                      <strong>{project.project_name}</strong>
                      <span className="health-badge health-red">{project.health_label}</span>
                    </div>
                    <div className="project-item-details">
                      <span>Client: {project.client_name}</span>
                      {project.risks && (
                        <span className="risks">Risks: {project.risks}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upcoming Deliveries */}
          {report.upcoming_deliveries.length > 0 && (
            <div className="section">
              <h3>Upcoming Deliveries ({report.upcoming_deliveries.length})</h3>
              <div className="deliveries-list">
                {report.upcoming_deliveries.map(delivery => (
                  <div key={delivery.project_id} className="delivery-item">
                    <div className="delivery-header">
                      <strong>{delivery.project_name}</strong>
                      <span className={`health-badge health-${delivery.health_status}`}>
                        {delivery.health_status === 'green' ? 'Healthy' : 
                         delivery.health_status === 'yellow' ? 'At Risk' : 'Critical'}
                      </span>
                    </div>
                    <div className="delivery-details">
                      <span>Client: {delivery.client_name}</span>
                      <span className="delivery-text">{delivery.next_delivery}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="report-footer">
            <small>
              Report generated: {new Date(report.generated_at).toLocaleString()}
              {report.generated_by && ` by ${report.generated_by}`}
            </small>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <p>No report data available. Click "Generate Report" to create a health report.</p>
        </div>
      )}
    </div>
  )
}

export default Reports
