'use client'

import { useState } from 'react'
import styles from './Sidebar.module.css'

const navItems = [
  { label: 'Dashboard',      icon: '⬡' },
  { label: 'Camera Network', icon: '◉' },
  { label: 'Vehicle Search', icon: '⊕' },
  { label: 'Timelines',      icon: '≡' },
]

export default function Sidebar() {
  const [active, setActive] = useState('Vehicle Search')

  return (
    <aside className={styles.sidebar}>
      <div className={styles.sectionLabel}>Navigation</div>

      {navItems.map((item) => (
        <div
          key={item.label}
          className={`${styles.navItem} ${active === item.label ? styles.active : ''}`}
          onClick={() => setActive(item.label)}
        >
          <span className={styles.icon}>{item.icon}</span>
          {item.label}
        </div>
      ))}

      <div className={styles.divider} />

      <div className={styles.sectionLabel}>Status</div>

      <div className={styles.statusItem}>
        <span className={`${styles.statusDot} ${styles.green}`} />
        <span>9 Cameras Active</span>
      </div>
      <div className={styles.statusItem}>
        <span className={`${styles.statusDot} ${styles.yellow}`} />
        <span>2 Alerts</span>
      </div>
    </aside>
  )
}