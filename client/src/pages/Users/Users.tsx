import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import api from '../../services/api'
import { RootState } from '../../store/store'
import './Users.css'

interface User {
  id: number
  email: string
  name: string
  role: string
  created_at: string
  updated_at?: string
}

const Users: React.FC = () => {
  const { user: currentUser } = useSelector((state: RootState) => state.auth)
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await api.get('/users/')
      setUsers(response.data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch users')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (userId: number) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return
    }

    try {
      await api.delete(`/users/${userId}`)
      setUsers(users.filter(u => u.id !== userId))
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete user')
    }
  }

  if (loading) {
    return <div className="users-container">Loading...</div>
  }

  if (error) {
    return <div className="users-container error-message">{error}</div>
  }

  return (
    <div className="users-container">
      <div className="users-header">
        <h2>User Management</h2>
        <p>Manage users and their roles</p>
      </div>

      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>
                  <span className={`role-badge role-${user.role}`}>
                    {user.role}
                  </span>
                </td>
                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                  {currentUser?.id !== user.id && (
                    <button
                      onClick={() => handleDelete(user.id)}
                      className="btn-delete"
                    >
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Users
