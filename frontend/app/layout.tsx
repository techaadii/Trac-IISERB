'use client'

import './globals.css'
import { createContext, useContext, useState } from 'react'
import Navbar  from '@/components/Navbar'
import Sidebar from '@/components/Sidebar'

// ── Shared navigation context ─────────────────────────────────────────────────
export type NavContextType = {
  activePage: string
  setActivePage: (page: string) => void
}

export const NavContext = createContext<NavContextType>({
  activePage: 'Vehicle Search',
  setActivePage: () => {},
})

export const useNav = () => useContext(NavContext)

// ── Layout ────────────────────────────────────────────────────────────────────
export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [activePage, setActivePage] = useState('Vehicle Search')

  return (
    <html lang="en">
      <body>
        <NavContext.Provider value={{ activePage, setActivePage }}>
          <Navbar />
          <div className="layout">
            <Sidebar active={activePage} onChange={setActivePage} />
            <main className="main-content">{children}</main>
          </div>
        </NavContext.Provider>
      </body>
    </html>
  )
}