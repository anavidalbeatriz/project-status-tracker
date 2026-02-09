import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import api from '../../services/api'

export interface ProjectStatus {
  id: number
  project_id: number
  is_on_scope: boolean | null
  is_on_time: boolean | null
  is_on_budget: boolean | null
  next_delivery: string | null
  risks: string | null
  updated_by: number
  updated_at: string
  updater?: {
    id: number
    name: string
    email: string
  }
}

export interface ProjectStatusCreate {
  project_id: number
  is_on_scope?: boolean | null
  is_on_time?: boolean | null
  is_on_budget?: boolean | null
  next_delivery?: string | null
  risks?: string | null
}

export interface ProjectStatusUpdate {
  is_on_scope?: boolean | null
  is_on_time?: boolean | null
  is_on_budget?: boolean | null
  next_delivery?: string | null
  risks?: string | null
}

interface ProjectStatusState {
  statuses: ProjectStatus[]
  currentStatus: ProjectStatus | null
  latestStatus: ProjectStatus | null
  loading: boolean
  error: string | null
}

const initialState: ProjectStatusState = {
  statuses: [],
  currentStatus: null,
  latestStatus: null,
  loading: false,
  error: null
}

// Fetch all project statuses for a project
export const fetchProjectStatuses = createAsyncThunk(
  'projectStatus/fetchProjectStatuses',
  async (projectId: number, { rejectWithValue }) => {
    try {
      const response = await api.get('/project-status/', {
        params: { project_id: projectId }
      })
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch project statuses')
    }
  }
)

// Fetch latest project status
export const fetchLatestProjectStatus = createAsyncThunk(
  'projectStatus/fetchLatestProjectStatus',
  async (projectId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/project-status/project/${projectId}/latest`)
      return response.data
    } catch (error: any) {
      // If no status exists, return null (not an error)
      if (error.response?.status === 404) {
        return null
      }
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch latest project status')
    }
  }
)

// Create new project status
export const createProjectStatus = createAsyncThunk(
  'projectStatus/createProjectStatus',
  async (statusData: ProjectStatusCreate, { rejectWithValue }) => {
    try {
      const response = await api.post('/project-status/', statusData)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create project status')
    }
  }
)

// Update project status
export const updateProjectStatus = createAsyncThunk(
  'projectStatus/updateProjectStatus',
  async ({ statusId, statusData }: { statusId: number; statusData: ProjectStatusUpdate }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/project-status/${statusId}`, statusData)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update project status')
    }
  }
)

// Delete project status
export const deleteProjectStatus = createAsyncThunk(
  'projectStatus/deleteProjectStatus',
  async (statusId: number, { rejectWithValue }) => {
    try {
      await api.delete(`/project-status/${statusId}`)
      return statusId
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete project status')
    }
  }
)

const projectStatusSlice = createSlice({
  name: 'projectStatus',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearCurrentStatus: (state) => {
      state.currentStatus = null
    },
    clearLatestStatus: (state) => {
      state.latestStatus = null
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch project statuses
      .addCase(fetchProjectStatuses.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchProjectStatuses.fulfilled, (state, action: PayloadAction<ProjectStatus[]>) => {
        state.loading = false
        state.statuses = action.payload
      })
      .addCase(fetchProjectStatuses.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      // Fetch latest project status
      .addCase(fetchLatestProjectStatus.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchLatestProjectStatus.fulfilled, (state, action: PayloadAction<ProjectStatus | null>) => {
        state.loading = false
        state.latestStatus = action.payload
      })
      .addCase(fetchLatestProjectStatus.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      // Create project status
      .addCase(createProjectStatus.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(createProjectStatus.fulfilled, (state, action: PayloadAction<ProjectStatus>) => {
        state.loading = false
        state.statuses.unshift(action.payload) // Add to beginning
        state.latestStatus = action.payload
      })
      .addCase(createProjectStatus.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      // Update project status
      .addCase(updateProjectStatus.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(updateProjectStatus.fulfilled, (state, action: PayloadAction<ProjectStatus>) => {
        state.loading = false
        const index = state.statuses.findIndex((s) => s.id === action.payload.id)
        if (index !== -1) {
          state.statuses[index] = action.payload
        }
        if (state.latestStatus?.id === action.payload.id) {
          state.latestStatus = action.payload
        }
      })
      .addCase(updateProjectStatus.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      // Delete project status
      .addCase(deleteProjectStatus.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(deleteProjectStatus.fulfilled, (state, action: PayloadAction<number>) => {
        state.loading = false
        state.statuses = state.statuses.filter((s) => s.id !== action.payload)
        if (state.latestStatus?.id === action.payload) {
          state.latestStatus = null
        }
      })
      .addCase(deleteProjectStatus.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
  }
})

export const { clearError, clearCurrentStatus, clearLatestStatus } = projectStatusSlice.actions
export default projectStatusSlice.reducer
