import React, { useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { uploadTranscription, clearError } from '../../store/slices/transcriptionSlice'
import { AppDispatch, RootState } from '../../store/store'
import './TranscriptionUpload.css'

interface TranscriptionUploadProps {
  projectId: number
  onUploadSuccess?: () => void
}

const TranscriptionUpload: React.FC<TranscriptionUploadProps> = ({ projectId, onUploadSuccess }) => {
  const dispatch = useDispatch<AppDispatch>()
  const { loading, error } = useSelector((state: RootState) => state.transcriptions)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const allowedExtensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm', '.mp4', '.avi', '.mov', '.mkv', '.txt', '.doc', '.docx', '.pdf']
  const maxSizeMB = 100

  const handleFileSelect = (file: File) => {
    // Validate file extension
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!allowedExtensions.includes(fileExt)) {
      alert(`File type not allowed. Allowed types: ${allowedExtensions.join(', ')}`)
      return
    }

    // Validate file size (100MB)
    if (file.size > maxSizeMB * 1024 * 1024) {
      alert(`File size exceeds maximum allowed size of ${maxSizeMB}MB`)
      return
    }

    setSelectedFile(file)
    dispatch(clearError())
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      return
    }

    try {
      await dispatch(uploadTranscription({ projectId, file: selectedFile })).unwrap()
      setSelectedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      if (onUploadSuccess) {
        onUploadSuccess()
      }
    } catch (err) {
      // Error is handled by Redux
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  return (
    <div className="transcription-upload">
      <h3>Upload Transcription</h3>
      
      {error && (
        <div className="error-message" onClick={() => dispatch(clearError())}>
          {error}
        </div>
      )}

      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileInputChange}
          accept={allowedExtensions.join(',')}
          style={{ display: 'none' }}
        />
        <div className="upload-content">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <p>Click to upload or drag and drop</p>
          <p className="upload-hint">
            Audio, Video, or Text files (max {maxSizeMB}MB)
          </p>
        </div>
      </div>

      {selectedFile && (
        <div className="selected-file">
          <div className="file-info">
            <span className="file-name">{selectedFile.name}</span>
            <span className="file-size">{formatFileSize(selectedFile.size)}</span>
          </div>
          <button
            onClick={() => {
              setSelectedFile(null)
              if (fileInputRef.current) {
                fileInputRef.current.value = ''
              }
            }}
            className="btn-remove"
          >
            Remove
          </button>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!selectedFile || loading}
        className="btn-upload"
      >
        {loading ? 'Uploading...' : 'Upload Transcription'}
      </button>
    </div>
  )
}

export default TranscriptionUpload
