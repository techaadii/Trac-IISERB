import { vehicles } from '@/lib/dummyData'


export default function VehicleTable() {
return (
<table className="table">
<thead>
<tr>
<th>Vehicle ID</th>
<th>Color</th>
<th>Camera</th>
<th>Time</th>
</tr>
</thead>
<tbody>
{vehicles.map(v => (
<tr key={v.id}>
<td>{v.id}</td>
<td>{v.color}</td>
<td>{v.camera}</td>
<td>{v.time}</td>
</tr>
))}
</tbody>
</table>
)
}