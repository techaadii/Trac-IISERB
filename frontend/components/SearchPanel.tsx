'use client'

import { useRef, useState } from 'react'
import { rootImages, vehicleTypes } from '@/lib/dummyData'
import styles from './SearchPanel.module.css'

type QueryImage = {
  name: string
  size: string
  url: string | null
}

type Props = {
  onSearch: () => void
}

export default function SearchPanel({ onSearch }: Props) {
  const [activeTab, setActiveTab] = useState<'upload' | 'browse' | 'text'>('upload')
  const [dragOver, setDragOver]   = useState(false)
  const [queryImage, setQueryImage] = useState<QueryImage | null>(null)
  const [filterType, setFilterType] = useState('All')
  const [filterFrom, setFilterFrom] = useState('')
  const [filterTo,   setFilterTo]   = useState('')
  const [textQuery,  setTextQuery]  = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  /* ── helpers ─────────────────────────────────────── */
  const applyFile = (file: File) => {
    setQueryImage({
      name: file.name,
      size: `${(file.size / 1024).toFixed(1)} KB`,
      url:  URL.createObjectURL(file),
    })
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file?.type.startsWith('image/')) applyFile(file)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) applyFile(file)
  }

  /** Dragging a root-camera thumbnail sets it as the query */
  const handleGridDragEnd = (img: (typeof rootImages)[0]) => {
    setQueryImage({ name: img.label, size: 'root camera', url: null })
    setActiveTab('upload')
  }

  const filteredImages = rootImages.filter(
    (img) => filterType === 'All' || img.type === filterType,
  )

  const canSearch =
    (activeTab === 'upload' && queryImage !== null) ||
    (activeTab === 'browse' && queryImage !== null) ||
    (activeTab === 'text'   && textQuery.trim().length > 0)

  const tabs = [
    { id: 'upload' as const, icon: '⬆', label: 'Upload Query Image'  },
    { id: 'browse' as const, icon: '⊞', label: 'Browse Root Camera'  },
    { id: 'text'   as const, icon: '◈', label: 'Text Description'     },
  ]

  return (
    <div className={styles.panel}>
      {/* ── Tab Bar ─────────────────────────────────── */}
      <div className={styles.tabBar}>
        {tabs.map((t) => (
          <button
            key={t.id}
            className={`${styles.tab} ${activeTab === t.id ? styles.tabActive : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            <span>{t.icon}</span> {t.label}
          </button>
        ))}
      </div>

      {/* ── Tab Body ────────────────────────────────── */}
      <div className={styles.tabBody}>

        {/* TAB 1 — Upload */}
        {activeTab === 'upload' && (
          <div>
            {!queryImage ? (
              <div
                className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileRef.current?.click()}
              >
                <span className={styles.dzIcon}>⊕</span>
                <span className={styles.dzLabel}>Add Query Image Here</span>
                <span className={styles.dzSub}>drag &amp; drop or click to browse · JPG, PNG, WEBP</span>
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  style={{ display: 'none' }}
                  onChange={handleFileInput}
                />
              </div>
            ) : (
              <div className={styles.queryPreview}>
                <div className={styles.queryThumb}>
                  {queryImage.url
                    ? <img src={queryImage.url} alt="query" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 6 }} />
                    : '🚗'}
                </div>
                <div className={styles.queryInfo}>
                  <div className={styles.queryName}>{queryImage.name}</div>
                  <div className={styles.queryMeta}>{queryImage.size}</div>
                </div>
                <button className={styles.removeBtn} onClick={() => setQueryImage(null)}>✕</button>
              </div>
            )}

            <div className={styles.actionRow}>
              <button className="btn btn-cyan" onClick={onSearch} disabled={!canSearch}>
                ⊕ Search Cameras
              </button>
              {queryImage && (
                <button className="btn btn-outline" onClick={() => setQueryImage(null)}>
                  ✕ Clear
                </button>
              )}
            </div>
          </div>
        )}

        {/* TAB 2 — Browse Root Camera */}
        {activeTab === 'browse' && (
          <div>
            <div className={styles.filterRow}>
              <div className="field">
                <label className="field-label">Vehicle Type</label>
                <select className="field-select" value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                  {vehicleTypes.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div className="field">
                <label className="field-label">Time From</label>
                <input type="time" className="field-input" value={filterFrom} onChange={(e) => setFilterFrom(e.target.value)} />
              </div>
              <div className="field">
                <label className="field-label">Time To</label>
                <input type="time" className="field-input" value={filterTo} onChange={(e) => setFilterTo(e.target.value)} />
              </div>
            </div>

            <p className={styles.dragHint}>↕ Drag any image below to use it as your query</p>

            {filteredImages.length > 0 ? (
              <div className={styles.imageGrid}>
                {filteredImages.map((img) => (
                  <div
                    key={img.id}
                    className={styles.imgCard}
                    draggable
                    onDragEnd={() => handleGridDragEnd(img)}
                    title="Drag to use as query"
                  >
                    <div className={styles.imgThumb} style={{ background: img.bg }}>🚗</div>
                    <div className={styles.imgMeta}>
                      <div className={styles.imgLabel}>{img.label}</div>
                      <div className={styles.imgType}>{img.type}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <span className="empty-icon">⊘</span>
                <span className="empty-text">No images match the current filters</span>
              </div>
            )}
          </div>
        )}

        {/* TAB 3 — Text Search */}
        {activeTab === 'text' && (
          <div className={styles.textArea}>
            <div className="field">
              <label className="field-label">Describe the Vehicle</label>
              <textarea
                className={styles.textarea}
                placeholder="e.g. Red Honda sedan, visible dent on left door, partial plate MP-09..."
                value={textQuery}
                onChange={(e) => setTextQuery(e.target.value)}
              />
            </div>

            <div className={styles.actionRow}>
              <button className="btn btn-cyan" onClick={onSearch} disabled={!canSearch}>
                ◈ Search by Description
              </button>
              {textQuery && (
                <button className="btn btn-outline" onClick={() => { setTextQuery(''); }}>
                  ✕ Clear
                </button>
              )}
            </div>

            {textQuery && (
              <div className={styles.tagRow}>
                {textQuery.split(' ').filter((w) => w.length > 3).slice(0, 6).map((w) => (
                  <span key={w} className="tag">{w.toLowerCase()}</span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}