import VehicleTable from '@/components/VehicleTable'


export default function Home() {
return (
<div className="fade-in">
<h1 className="title">Vehicle Tracking Dashboard</h1>
<p className="subtitle">
Multi-camera retrieval with human-in-the-loop verification
</p>
<VehicleTable />
</div>
)
}