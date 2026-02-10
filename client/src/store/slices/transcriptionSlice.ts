import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

interface Transcription {
  id: number
  project_id: number
  file_path?: string
  file_name?: string
  file_type?: string
  file_size?: number
  raw_text?: string
  processed_at?: string
  created_by: number
  created_at: string
  project?: {
    id: number
    name: string
  }
  creator?: {
    id: number
    name: string
    email: string
  }
}

interface TranscriptionState {
  transcriptions: Transcription[]
  currentTranscription: Transcription | null
  loading: boolean
  error: string | null
}

const initialState: TranscriptionState = {
  transcriptions: [],
  currentTranscription: null,
  loading: false,
  error: null,
}

// Async thunks
export const fetchTranscriptions = createAsyncThunk(
  'transcriptions/fetchTranscriptions',
  async (projectId: number | undefined, { rejectWithValue }) => {
    try {
      const params = projectId ? `?project_id=${projectId}` : ''
      const response = await api.get(`/transcriptions${params}`)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch transcriptions')
    }
  }
)

export const uploadTranscription = createAsyncThunk(
  'transcriptions/uploadTranscription',
  async ({ projectId, file }: { projectId: number; file: File }, { rejectWithValue }) => {
    try {
      const formData = new FormData()
      formData.append('project_id', projectId.toString())
      formData.append('file', file)
      
      const response = await api.post('/transcriptions/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to upload transcription')
    }
  }
)

export const deleteTranscription = createAsyncThunk(
  'transcriptions/deleteTranscription',
  async (transcriptionId: number, { rejectWithValue }) => {
    try {
      await api.delete(`/transcriptions/${transcriptionId}`)
      return transcriptionId
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete transcription')
    }
  }
)

const transcriptionSlice = createSlice({
  name: 'transcriptions',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearCurrentTranscription: (state) => {
      state.currentTranscription = null
    },
  },
  extraReducers: (builder) => {
    // Fetch transcriptions
    builder
      .addCase(fetchTranscriptions.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchTranscriptions.fulfilled, (state, action) => {
        state.loading = false
        state.transcriptions = action.payload
      })
      .addCase(fetchTranscriptions.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Upload transcription
    builder
      .addCase(uploadTranscription.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(uploadTranscription.fulfilled, (state, action) => {
        state.loading = false
        state.transcriptions.push(action.payload)
      })
      .addCase(uploadTranscription.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Delete transcription
    builder
      .addCase(deleteTranscription.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(deleteTranscription.fulfilled, (state, action) => {
        state.loading = false
        state.transcriptions = state.transcriptions.filter(t => t.id !== action.payload)
      })
      .addCase(deleteTranscription.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
  },
})

export const { clearError, clearCurrentTranscription } = transcriptionSlice.actions
export default transcriptionSlice.reducer
