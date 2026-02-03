import './globals.css'
import Navbar from '@/components/Navbar'
import Sidebar from '@/components/Sidebar'


export const metadata = {
title: 'Vehicle Tracking System | IISER Bhopal',
description: 'Multi-camera vehicle tracking dashboard',
}


export default function RootLayout({ children }: { children: React.ReactNode }) {
return (
<html lang="en">
<body>
<Navbar />
<div className="layout">
<Sidebar />
<main className="content">{children}</main>
</div>
</body>
</html>)}