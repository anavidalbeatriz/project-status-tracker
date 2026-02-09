import React, { useState, FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { createClient, clearError } from '../../store/slices/clientSlice'
import { AppDispatch, RootState } from '../../store/store'
import './ClientForm.css'

const ClientForm: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const dispatch = useDispatch<AppDispatch>()
  const { loading, error } = useSelector((state: RootState) => state.clients)

  const [name, setName] = useState('')
  const fromProject = searchParams.get('from') === 'project'

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    dispatch(clearError())

    try {
      await dispatch(createClient({ name })).unwrap()
      if (fromProject) {
        navigate('/projects/new')
      } else {
        navigate('/clients')
      }
    } catch (err) {
      // Error is handled by Redux
    }
  }

  return (
    <div className="client-form-container">
      <div className="client-form-header">
        <h2>Create New Client</h2>
        <button 
          onClick={() => navigate(fromProject ? '/projects/new' : '/clients')} 
          className="btn-back"
        >
          ← Back {fromProject ? 'to Project Form' : 'to Clients'}
        </button>
      </div>

      <div className="client-form-card">
        {error && (
          <div className="error-message" onClick={() => dispatch(clearError())}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Client Name *</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={loading}
              placeholder="Enter client name"
            />
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              onClick={() => navigate(fromProject ? '/projects/new' : '/clients')} 
              className="btn-cancel" 
              disabled={loading}
            >
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Creating...' : 'Create Client'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ClientForm
