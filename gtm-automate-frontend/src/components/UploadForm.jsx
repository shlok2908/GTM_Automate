import React, { useState } from 'react'

const PIXEL_OPTIONS = [
  { value: 'google_conversion', label: 'Google Conversion' },
  { value: 'google_remarketing', label: 'Google Remarketing' },
  { value: 'facebook_pixel', label: 'Facebook / Meta' },
  { value: 'bing', label: 'Bing' },
  { value: 'other', label: 'Other' }
]

// Helper function to filter out unwanted status lines
function filterSteps(steps = []) {
  return steps.filter(step => {
    const line = String(step).trim().toLowerCase()
    // Filter out verbose status information
    if (line.startsWith('status:')) return false
    if (line.startsWith('created =>')) return false
    if (line.startsWith('workspace =>')) return false
    if (line.startsWith('workspace url:') && line.includes('n/a')) return false
    if (line.startsWith('errors:')) return false
    if (line.startsWith('- no gtm container id provided')) return false
    if (line.startsWith('no gtm container id provided')) return false
    return true
  })
}

// Helper function to extract and render URLs as clickable links
function renderWithLinks(text) {
  if (!text) return null
  
  const urlRegex = /(https?:\/\/[^\s]+)/g
  const parts = String(text).split(urlRegex)
  
  return parts.map((part, idx) => {
    if (part.match(urlRegex)) {
      return (
        <a 
          key={idx} 
          href={part} 
          target="_blank" 
          rel="noopener noreferrer"
        >
          {part}
        </a>
      )
    }
    return part
  })
}

export default function UploadForm() {
  const [pixel, setPixel] = useState('google_conversion')
  const [containerId, setContainerId] = useState('')
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState(null)
  const [steps, setSteps] = useState([])
  const [uploading, setUploading] = useState(false)

  function onFileChange(e) {
    setFile(e.target.files[0] || null)
    setStatus(null)
    setSteps([])
  }

  async function onSubmit(e) {
    e.preventDefault()
    if (!file) {
      setStatus({ type: 'error', message: 'Please select a file to upload.' })
      return
    }

    setUploading(true)
    setStatus({ type: 'info', message: 'Uploading file and starting GTM automation...' })
    setSteps([])

    try {
      const form = new FormData()
      form.append('pixel', pixel)
      form.append('container_id', containerId)
      form.append('file', file)

      // Change this URL if your backend listens on a different path/port
      const res = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: form
      })

      const data = await res.json().catch(() => null)

      if (!res.ok) {
        const msg = data?.message || data?.error || `Server returned ${res.status}`
        setStatus({ type: 'error', message: msg })
        // Filter out verbose status lines for errors
        setSteps(filterSteps(data?.steps || data?.stderr || []))
        return
      }

      // For success, filter steps and only show URLs if they exist
      const filteredSteps = filterSteps(data?.steps || [])
      // Extract URLs from steps for success message
      const urlSteps = filteredSteps.filter(step => /https?:\/\//.test(String(step)))
      
      setStatus({ type: 'success', message: data.message || 'Uploaded and processed successfully.' })
      // Only show steps that contain URLs for success
      setSteps(urlSteps.length > 0 ? urlSteps : [])
    } catch (err) {
      setStatus({ type: 'error', message: err.message || 'Upload failed.' })
    } finally {
      setUploading(false)
    }
  }

  return (
    <form className="upload-form" onSubmit={onSubmit}>
      <header>
        <h1>GTM Automation — Upload</h1>
      </header>
      <div className="form-header">
        <div>
          <p className="eyebrow">GTM Workspace Automation</p>
          <p className="lede">Attach your feed, pick the tag style, and we will prep a clean workspace for review.</p>
        </div>
      
      </div>

      <div className="form-grid">
        <label className="field">
          <span>GTM Container ID</span>
          <input
            type="text"
            placeholder="e.g. 237397345 or GTM-XXXXXXX"
            value={containerId}
            onChange={e => setContainerId(e.target.value)}
          />
        </label>

        <label className="field">
          <span>Pixel Tag Type</span>
          <select value={pixel} onChange={e => setPixel(e.target.value)}>
            {PIXEL_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </label>

        <label className="field full">
          <span>Choose file (JSON / XLSX / XML)</span>
          <input type="file" accept=".json,.xlsx,.xls,.xml" onChange={onFileChange} />
        </label>
      </div>

      <div className="actions">
        <button type="submit" disabled={uploading}>{uploading ? 'Uploading...' : 'Upload & Update GTM'}</button>
      </div>

      {status && (
        <div className={`status ${status.type}`}>
          {renderWithLinks(status.message)}
        </div>
      )}

      {steps.length > 0 && (
        <ul className="status-steps">
          {steps.map((step, idx) => (
            <li key={idx}>{renderWithLinks(step)}</li>
          ))}
        </ul>
      )}
    </form>
  )
}
