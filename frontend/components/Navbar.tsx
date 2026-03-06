import Image from 'next/image'
import styles from './Navbar.module.css'

export default function Navbar() {
  return (
    <nav className={styles.navbar}>
      <div className={styles.navLeft}>
        <div className={styles.brandIcon}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" strokeWidth="2">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
          </svg>
        </div>
        <div>
          {/* Swap these Images back in once you have the actual logo files */}
          {/* <Image src="/iiser_logo.png" alt="IISER" width={50} height={40} /> */}
          <div className={styles.brandTitle}>
            IISERB<span className={styles.dot}>·</span>TRAC
          </div>
          <div className={styles.brandSub}>IISER Bhopal · Research Dashboard</div>
        </div>
      </div>

      <div className={styles.navRight}>
        <div className={styles.navBadge}>
          <span className={styles.navDot} />
          SYSTEM ONLINE
        </div>
        {/* <Image src="/lab_logo.png" alt="Lab" width={120} height={36} /> */}
      </div>
    </nav>
  )
}
