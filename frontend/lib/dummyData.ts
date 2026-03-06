export const vehicles = [
  { id: 'VH-001', color: 'Red',    camera: 'CAM-03', time: '08:14:22', type: 'Sedan',    confidence: 94 },
  { id: 'VH-002', color: 'White',  camera: 'CAM-07', time: '08:21:05', type: 'SUV',      confidence: 87 },
  { id: 'VH-003', color: 'Black',  camera: 'CAM-01', time: '08:33:41', type: 'Hatchback',confidence: 91 },
  { id: 'VH-004', color: 'Blue',   camera: 'CAM-05', time: '08:45:18', type: 'Sedan',    confidence: 78 },
  { id: 'VH-005', color: 'Silver', camera: 'CAM-09', time: '09:02:33', type: 'Truck',    confidence: 85 },
]

export const rootImages = [
  { id: 1, label: 'CAM-01 · 08:10', type: 'Sedan',     bg: '#1e2d3d' },
  { id: 2, label: 'CAM-01 · 08:22', type: 'SUV',       bg: '#1a2535' },
  { id: 3, label: 'CAM-01 · 08:35', type: 'Hatchback', bg: '#202e40' },
  { id: 4, label: 'CAM-01 · 09:00', type: 'Truck',     bg: '#1e2d3d' },
  { id: 5, label: 'CAM-01 · 09:15', type: 'Sedan',     bg: '#1a2535' },
  { id: 6, label: 'CAM-01 · 09:30', type: 'SUV',       bg: '#202e40' },
]

export const vehicleTypes = ['All', 'Sedan', 'SUV', 'Hatchback', 'Truck']

export const colorMap: Record<string, string> = {
  Red:    '#ef4444',
  White:  '#f1f5f9',
  Black:  '#374151',
  Blue:   '#3b82f6',
  Silver: '#94a3b8',
}

export const stats = [
  { label: 'Active Cameras',   value: '9',   delta: '+2 today',           cyan: false },
  { label: 'Vehicles Tracked', value: '142', delta: '+18 today',          cyan: false },
  { label: 'Matches Found',    value: '37',  delta: 'last 24h',           cyan: true  },
  { label: 'Avg Confidence',   value: '87%', delta: '↑ 3% vs yesterday', cyan: false },
]
