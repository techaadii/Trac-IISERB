'use client'

import { useState } from 'react'
import { useNav }    from './layout'
import LiveView      from '@/components/LiveView'
import SearchPanel   from '@/components/SearchPanel'
import StatsRow      from '@/components/StatsRow'
import VehicleTable  from '@/components/VehicleTable'
import styles        from './page.module.css'

export default function Home() {
  const { activePage }          = useNav()
  const [searched, setSearched] = useState(false)

  if (activePage === 'Live Cameras') {
    return (
      <div className={`${styles.page} fade-in`}>
        <LiveView />
      </div>
    )
  }

  return (
    <div className={`${styles.page} fade-in`}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          Vehicle <span className={styles.titleAccent}>Tracking</span> Dashboard
        </h1>
        <p className={styles.subtitle}>
          // multi-camera retrieval · HMM-guided sequential search · IISER Bhopal
        </p>
      </div>

      <StatsRow />
      <SearchPanel onSearch={() => setSearched(true)} />

      <div>
        <div className="section-header">
          <span className="section-title">Query Results</span>
          {searched && <span className="count-badge">5 matches</span>}
        </div>
        {searched ? (
          <div className="fade-in"><VehicleTable /></div>
        ) : (
          <div className="empty-state" style={{ background:'var(--surface)', border:'1px solid var(--border)', borderRadius:10 }}>
            <span className="empty-icon">⊡</span>
            <span className="empty-text">Run a search to see matched vehicles</span>
          </div>
        )}
      </div>
    </div>
  )
}