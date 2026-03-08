'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import styles from './LiveView.module.css'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const POLL_INTERVAL = 15_000   // ms between status polls
const SNAPSHOT_REFRESH = 5_000 // ms between snapshot refreshes per camera

type CameraInfo = {
  camera_id: string
  label: string
  ip: string
  online: boolean
  last_checked: number
  latency_ms: number | null
  snapshot_url: string
  mjpeg_url: string
}

type StatusPayload = {
  online_count: number
  offline_count: number
  total: number
  cameras: CameraInfo[]
}

// ── Single camera tile ─────────────────────────────────────────────────────

function CameraTile({
  cam,
  expanded,
  onClick,
}: {
  cam: CameraInfo
  expanded: boolean
  onClick: () => void
}) {
  const [imgSrc, setImgSrc]     = useState<string | null>(null)
  const [imgError, setImgError] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchSnapshot = useCallback(() => {
    if (!cam.online) return
    // Cache-bust so browser doesn't serve stale snapshot
    setImgSrc(`${API_BASE}${cam.snapshot_url}?t=${Date.now()}`)
    setImgError(false)
  }, [cam.online, cam.snapshot_url])

  useEffect(() => {
    fetchSnapshot()
    timerRef.current = setInterval(fetchSnapshot, SNAPSHOT_REFRESH)
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [fetchSnapshot])

  const lastSeen = cam.last_checked
    ? new Date(cam.last_checked * 1000).toLocaleTimeString()
    : '—'

  return (
    <div
      className={`${styles.tile} ${cam.online ? styles.online : styles.offline} ${expanded ? styles.expanded : ''}`}
      onClick={onClick}
      title={expanded ? 'Click to collapse' : 'Click to expand'}
    >
      {/* Status bar */}
      <div className={styles.tileHeader}>
        <div className={styles.tileId}>{cam.camera_id}</div>
        <div className={`${styles.statusPill} ${cam.online ? styles.pillOnline : styles.pillOffline}`}>
          <span className={styles.statusLed} />
          {cam.online ? 'LIVE' : 'OFFLINE'}
        </div>
      </div>

      {/* Feed area */}
      <div className={styles.feedArea}>
        {cam.online && imgSrc && !imgError ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={imgSrc}
            alt={cam.label}
            className={styles.feedImg}
            onError={() => setImgError(true)}
          />
        ) : cam.online && !imgError ? (
          <div className={styles.feedPlaceholder}>
            <span className={styles.loadingDot} />
            <span className={styles.loadingDot} style={{ animationDelay: '0.2s' }} />
            <span className={styles.loadingDot} style={{ animationDelay: '0.4s' }} />
          </div>
        ) : (
          <div className={styles.offlinePlaceholder}>
            <div className={styles.offlineIcon}>◎</div>
            <div className={styles.offlineText}>No Signal</div>
          </div>
        )}

        {/* Scan-line overlay */}
        <div className={styles.scanLines} />

        {/* Corner brackets */}
        <div className={`${styles.corner} ${styles.tl}`} />
        <div className={`${styles.corner} ${styles.tr}`} />
        <div className={`${styles.corner} ${styles.bl}`} />
        <div className={`${styles.corner} ${styles.br}`} />
      </div>

      {/* Footer meta */}
      <div className={styles.tileFooter}>
        <span className={styles.tileLabel}>{cam.label}</span>
        <span className={styles.tileMeta}>
          {cam.online
            ? `${cam.latency_ms ?? '—'}ms · ${lastSeen}`
            : `Last seen ${lastSeen}`}
        </span>
      </div>
    </div>
  )
}

// ── Main LiveView component ────────────────────────────────────────────────

export default function LiveView() {
  const [status, setStatus]       = useState<StatusPayload | null>(null)
  const [expandedId, setExpanded] = useState<string | null>(null)
  const [loading, setLoading]     = useState(true)
  const [lastRefresh, setLastRefresh] = useState<string>('')

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/live/status`)
      if (!res.ok) throw new Error('Failed')
      const data: StatusPayload = await res.json()
      setStatus(data)
      setLastRefresh(new Date().toLocaleTimeString())
    } catch {
      // keep stale data, show no-signal state per camera
    } finally {
      setLoading(false)
    }
  }, [])

  const forceRefresh = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/live/refresh`, { method: 'POST' })
      const data: StatusPayload = await res.json()
      setStatus(data)
      setLastRefresh(new Date().toLocaleTimeString())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    const timer = setInterval(fetchStatus, POLL_INTERVAL)
    return () => clearInterval(timer)
  }, [fetchStatus])

  const handleTileClick = (id: string) => {
    setExpanded(prev => (prev === id ? null : id))
  }

  if (loading && !status) {
    return (
      <div className={styles.loadingState}>
        <div className={styles.loadingRing} />
        <span>Connecting to camera network…</span>
      </div>
    )
  }

  const cameras = status?.cameras ?? []
  const onlineCount  = status?.online_count  ?? 0
  const offlineCount = status?.offline_count ?? 0
  const total        = status?.total         ?? 0

  return (
    <div className={styles.liveView}>

      {/* ── Header bar ────────────────────────────────────────── */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.headerTitle}>
            <span className={styles.liveIndicator} />
            Live Camera Network
          </div>
          <div className={styles.headerSub}>
            {lastRefresh && `Last refreshed ${lastRefresh}`}
          </div>
        </div>

        <div className={styles.headerStats}>
          <div className={styles.statChip}>
            <span className={styles.chipDot} style={{ background: 'var(--success)' }} />
            <span className={styles.chipVal}>{onlineCount}</span>
            <span className={styles.chipLabel}>Online</span>
          </div>
          <div className={styles.statChip}>
            <span className={styles.chipDot} style={{ background: 'var(--danger)' }} />
            <span className={styles.chipVal}>{offlineCount}</span>
            <span className={styles.chipLabel}>Offline</span>
          </div>
          <div className={styles.statChip}>
            <span className={styles.chipDot} style={{ background: 'var(--text-dim)' }} />
            <span className={styles.chipVal}>{total}</span>
            <span className={styles.chipLabel}>Total</span>
          </div>

          <button className={`btn btn-outline ${styles.refreshBtn}`} onClick={forceRefresh}>
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* ── Progress bar: online ratio ────────────────────────── */}
      <div className={styles.onlineBar}>
        <div
          className={styles.onlineFill}
          style={{ width: total > 0 ? `${(onlineCount / total) * 100}%` : '0%' }}
        />
      </div>

      {/* ── Camera grid ──────────────────────────────────────── */}
      {expandedId ? (
        // Expanded single view
        <div className={styles.expandedWrapper}>
          {cameras.filter(c => c.camera_id === expandedId).map(cam => (
            <CameraTile
              key={cam.camera_id}
              cam={cam}
              expanded
              onClick={() => setExpanded(null)}
            />
          ))}
          {/* Thumbnail strip of others */}
          <div className={styles.thumbStrip}>
            {cameras.filter(c => c.camera_id !== expandedId).map(cam => (
              <CameraTile
                key={cam.camera_id}
                cam={cam}
                expanded={false}
                onClick={() => handleTileClick(cam.camera_id)}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className={styles.grid}>
          {cameras.map(cam => (
            <CameraTile
              key={cam.camera_id}
              cam={cam}
              expanded={false}
              onClick={() => handleTileClick(cam.camera_id)}
            />
          ))}
        </div>
      )}

      {cameras.length === 0 && (
        <div className="empty-state">
          <span className="empty-icon">◎</span>
          <span className="empty-text">No cameras configured</span>
        </div>
      )}
    </div>
  )
}