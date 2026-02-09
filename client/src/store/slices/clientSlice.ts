import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import api from '../../services/api'

interface Project {
  id: number
  name: string
  client_id: number
  created_by: number
  created_at: string
  updated_at?: string
}

interface Client {
  id: number
  name: string
  created_at: string
  updated_at?: string
  projects?: Project[]
}

interface ClientState {
  clients: Client[]
  loading: boolean
  error: string | null
}

const initialState: ClientState = {
  clients: [],
  loading: false,
  error: null,
}

// Async thunks
export const fetchClients = createAsyncThunk(
  'clients/fetchClients',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/clients/')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch clients')
    }
  }
)

export const createClient = createAsyncThunk(
  'clients/createClient',
  async (clientData: { name: string }, { rejectWithValue }) => {
    try {
      const response = await api.post('/clients/', clientData)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create client')
    }
  }
)

const clientSlice = createSlice({
  name: 'clients',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    // Fetch clients
    builder
      .addCase(fetchClients.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchClients.fulfilled, (state, action) => {
        state.loading = false
        state.clients = action.payload
      })
      .addCase(fetchClients.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Create client
    builder
      .addCase(createClient.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(createClient.fulfilled, (state, action) => {
        state.loading = false
        state.clients.push(action.payload)
      })
      .addCase(createClient.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
  },
})

export const { clearError } = clientSlice.actions
export default clientSlice.reducer
