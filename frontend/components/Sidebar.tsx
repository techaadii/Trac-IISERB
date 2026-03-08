'use client'

import { useEffect, useState } from 'react'
import styles from './Sidebar.module.css'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

const navItems = [
  { label: 'Dashboard',      icon: '⬡' },
  { label: 'Camera Network', icon: '◉' },
  { label: 'Vehicle Search', icon: '⊕' },
  { label: 'Live Cameras',   icon: '▶' },
  { label: 'Timelines',      icon: '≡' },
]

type Props = {
  active?: string
  onChange?: (label: string) => void
}

export default function Sidebar({ active = 'Vehicle Search', onChange }: Props) {
  const [onlineCount,  setOnlineCount]  = useState<number | null>(null)
  const [offlineCount, setOfflineCount] = useState<number | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res  = await fetch(`${API_BASE}/api/live/status`)
        const data = await res.json()
        setOnlineCount(data.online_count)
        setOfflineCount(data.offline_count)
      } catch {
        // backend not yet running — show placeholder
      }
    }
    fetchStatus()
    const t = setInterval(fetchStatus, 15_000)
    return () => clearInterval(t)
  }, [])

  return (
    <aside className={styles.sidebar}>
      <div className={styles.sectionLabel}>Navigation</div>

      {navItems.map((item) => (
        <div
          key={item.label}
          className={`${styles.navItem} ${active === item.label ? styles.active : ''}`}
          onClick={() => onChange?.(item.label)}
        >
          <span className={styles.icon}>{item.icon}</span>
          <span>{item.label}</span>
          {item.label === 'Live Cameras' && onlineCount !== null && (
            <span className={styles.liveBadge}>{onlineCount} live</span>
          )}
        </div>
      ))}

      <div className={styles.divider} />

      <div className={styles.sectionLabel}>Status</div>

      <div className={styles.statusItem}>
        <span className={`${styles.statusDot} ${styles.green}`} />
        <span>
          {onlineCount !== null ? `${onlineCount} Camera${onlineCount !== 1 ? 's' : ''} Online` : '— Cameras Online'}
        </span>
      </div>
      <div className={styles.statusItem}>
        <span className={`${styles.statusDot} ${styles.yellow}`} />
        <span>
          {offlineCount !== null ? `${offlineCount} Camera${offlineCount !== 1 ? 's' : ''} Offline` : '— Cameras Offline'}
        </span>
      </div>
    </aside>
  )
}