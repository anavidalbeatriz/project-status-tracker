import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export interface ProjectHealthMetrics {
  project_id: number
  project_name: string
  client_name: string
  health_status: string
  health_label: string
  is_on_scope: boolean | null
  is_on_time: boolean | null
  is_on_budget: boolean | null
  next_delivery: string | null
  risks: string | null
  last_updated: string | null
  green_count: number
}

export interface ClientHealthSummary {
  client_id: number
  client_name: string
  total_projects: number
  healthy_projects: number
  at_risk_projects: number
  critical_projects: number
  no_status_projects: number
  health_percentage: number
}

export interface OverallHealthMetrics {
  total_projects: number
  healthy_projects: number
  at_risk_projects: number
  critical_projects: number
  no_status_projects: number
  overall_health_percentage: number
  scope_compliance: number
  time_compliance: number
  budget_compliance: number
}

export interface UpcomingDelivery {
  project_id: number
  project_name: string
  client_name: string
  next_delivery: string
  health_status: string
  last_updated: string
}

export interface ProjectHealthReport {
  generated_at: string
  generated_by: string | null
  overall_metrics: OverallHealthMetrics
  project_metrics: ProjectHealthMetrics[]
  client_summaries: ClientHealthSummary[]
  upcoming_deliveries: UpcomingDelivery[]
  projects_at_risk: ProjectHealthMetrics[]
  critical_projects: ProjectHealthMetrics[]
}

export interface ReportFilters {
  client_ids?: number[]
  health_status?: string
  date_from?: string
  date_to?: string
  include_no_status?: boolean
}

interface ReportState {
  report: ProjectHealthReport | null
  loading: boolean
  error: string | null
}

const initialState: ReportState = {
  report: null,
  loading: false,
  error: null
}

// Generate project health report
export const generateReport = createAsyncThunk(
  'report/generateReport',
  async (filters: ReportFilters | undefined, { rejectWithValue }) => {
    try {
      const params = new URLSearchParams()
      
      if (filters?.client_ids && filters.client_ids.length > 0) {
        filters.client_ids.forEach(id => params.append('client_ids', id.toString()))
      }
      if (filters?.health_status) {
        params.append('health_status', filters.health_status)
      }
      if (filters?.date_from) {
        params.append('date_from', filters.date_from)
      }
      if (filters?.date_to) {
        params.append('date_to', filters.date_to)
      }
      if (filters?.include_no_status !== undefined) {
        params.append('include_no_status', filters.include_no_status.toString())
      }
      
      const queryString = params.toString()
      const url = `/reports/health${queryString ? `?${queryString}` : ''}`
      const response = await api.get(url)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to generate report')
    }
  }
)

const reportSlice = createSlice({
  name: 'report',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearReport: (state) => {
      state.report = null
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(generateReport.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(generateReport.fulfilled, (state, action) => {
        state.loading = false
        state.report = action.payload
      })
      .addCase(generateReport.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
  }
})

export const { clearError, clearReport } = reportSlice.actions
export default reportSlice.reducer
