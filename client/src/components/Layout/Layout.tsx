import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { logout } from '../../store/slices/authSlice'
import { AppDispatch, RootState } from '../../store/store'
import './Layout.css'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth)

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <div className="layout">
      <header className="layout-header">
        <h1>Project Status Tracker</h1>
        <nav>
          {isAuthenticated ? (
            <div className="nav-user">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/projects" className="nav-link">Projects</Link>
              <Link to="/clients" className="nav-link">Clients</Link>
              <Link to="/reports" className="nav-link">Reports</Link>
              {user?.role === 'admin' && (
                <Link to="/users" className="nav-link">Users</Link>
              )}
              <span>Welcome, {user?.name}</span>
              <button onClick={handleLogout} className="btn-logout">
                Logout
              </button>
            </div>
          ) : (
            <div className="nav-auth">
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </div>
          )}
        </nav>
      </header>
      <main className="layout-main">
        {children}
      </main>
      <footer className="layout-footer">
        <p>&copy; 2024 Project Status Tracker</p>
      </footer>
    </div>
  )
}

export default Layout
