import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import projectReducer from './slices/projectSlice'
import clientReducer from './slices/clientSlice'
import transcriptionReducer from './slices/transcriptionSlice'
import projectStatusReducer from './slices/projectStatusSlice'
import reportReducer from './slices/reportSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    projects: projectReducer,
    clients: clientReducer,
    transcriptions: transcriptionReducer,
    projectStatus: projectStatusReducer,
    report: reportReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
