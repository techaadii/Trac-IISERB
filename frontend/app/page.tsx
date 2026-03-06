'use client'

import { useState } from 'react'
import StatsRow    from '@/components/StatsRow'
import SearchPanel from '@/components/SearchPanel'
import VehicleTable from '@/components/VehicleTable'
import styles from './page.module.css'

export default function Home() {
  const [searched, setSearched] = useState(false)

  return (
    <div className={`${styles.page} fade-in`}>
      {/* Header */}
      <div className={styles.header}>
        <h1 className={styles.title}>
          Vehicle <span className={styles.titleAccent}>Tracking</span> Dashboard
        </h1>
        <p className={styles.subtitle}>
          // multi-camera retrieval · human-in-the-loop verification
        </p>
      </div>

      {/* Stats */}
      <StatsRow />

      {/* Search Panel */}
      <SearchPanel onSearch={() => setSearched(true)} />

      {/* Results */}
      <div>
        <div className="section-header">
          <span className="section-title">Query Results</span>
          {searched && <span className="count-badge">5 matches</span>}
        </div>

        {searched ? (
          <div className="fade-in">
            <VehicleTable />
          </div>
        ) : (
          <div
            className="empty-state"
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 10,
            }}
          >
            <span className="empty-icon">⊡</span>
            <span className="empty-text">Run a search to see matched vehicles</span>
          </div>
        )}
      </div>
    </div>
  )
}