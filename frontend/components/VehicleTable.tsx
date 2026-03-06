import { vehicles, colorMap } from '@/lib/dummyData'
import styles from './VehicleTable.module.css'

export default function VehicleTable() {
  return (
    <div className={styles.wrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Vehicle ID</th>
            <th>Type</th>
            <th>Color</th>
            <th>Camera</th>
            <th>Timestamp</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {vehicles.map((v) => (
            <tr key={v.id}>
              <td>
                <span className={styles.tdId}>{v.id}</span>
              </td>
              <td>{v.type}</td>
              <td>
                <span className={styles.colorDot}>
                  <span
                    className={styles.dot}
                    style={{ background: colorMap[v.color] ?? '#888' }}
                  />
                  {v.color}
                </span>
              </td>
              <td>
                <span className={`${styles.tdMono} mono`}>{v.camera}</span>
              </td>
              <td>
                <span className={`${styles.tdTime} mono`}>{v.time}</span>
              </td>
              <td>
                <div className={styles.confBar}>
                  <div className={styles.confTrack}>
                    <div
                      className={styles.confFill}
                      style={{ width: `${v.confidence}%` }}
                    />
                  </div>
                  <span className={`${styles.confVal} mono`}>{v.confidence}%</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}