import Image from 'next/image'


export default function Navbar() {
return (
<nav className="navbar">
<div className="nav-left">
<Image src="/iiser_logo.png" alt="IISER" width={50} height={40} />
<div>
<h2>IISERB-Trac</h2>
<span className="nav-sub">IISER Bhopal · Research Dashboard</span>
</div>
</div>


<Image src="/lab_logo.png" alt="Lab" width={200
} height={40} />
</nav>
)
}