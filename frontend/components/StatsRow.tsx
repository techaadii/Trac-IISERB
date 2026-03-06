import { stats } from '@/lib/dummyData'
import styles from './StatsRow.module.css'

export default function StatsRow() {
  return (
    <div className={styles.grid}>
      {stats.map((s) => (
        <div key={s.label} className={styles.card}>
          <div className={styles.label}>{s.label}</div>
          <div className={`${styles.value} ${s.cyan ? styles.cyan : ''}`}>{s.value}</div>
          <div className={styles.delta}>{s.delta}</div>
        </div>
      ))}
    </div>
  )
}