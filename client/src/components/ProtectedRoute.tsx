import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { fetchCurrentUser } from '../store/slices/authSlice'
import { AppDispatch, RootState } from '../store/store'

interface ProtectedRouteProps {
  children: React.ReactNode
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const dispatch = useDispatch<AppDispatch>()
  const { isAuthenticated, token, loading } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    if (token && !isAuthenticated) {
      dispatch(fetchCurrentUser())
    }
  }, [token, isAuthenticated, dispatch])

  if (loading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
