# IISERB-TRAC · Redesigned Frontend

## File Structure

```
trac-dashboard/
├── app/
│   ├── globals.css          ← CSS variables + shared utility classes
│   ├── layout.tsx           ← Root layout (Navbar + Sidebar wrapper)
│   ├── page.tsx             ← Main dashboard page (client state for search)
│   └── page.module.css
│
├── components/
│   ├── Navbar.tsx           ← Top bar with brand + status badge
│   ├── Navbar.module.css
│   ├── Sidebar.tsx          ← Nav items + status indicators
│   ├── Sidebar.module.css
│   ├── StatsRow.tsx         ← 4 KPI stat cards
│   ├── StatsRow.module.css
│   ├── SearchPanel.tsx      ← 3-tab search (upload / browse / text)
│   ├── SearchPanel.module.css
│   ├── VehicleTable.tsx     ← Results table with confidence bars
│   └── VehicleTable.module.css
│
└── lib/
    └── dummyData.ts         ← vehicles, rootImages, stats, colorMap
```

## Setup

```bash
# Install deps (if not already done)
npm install

# Run dev server
npm run dev
```

## Notes

- Font: **Rajdhani** (display) + **JetBrains Mono** (code/labels) — loaded via Google Fonts in globals.css
- CSS variables are declared in `globals.css :root` and used across all module files
- `Navbar.tsx` has commented-out `<Image>` tags — uncomment and point to your actual logo files in `/public`
- `SearchPanel` accepts an `onSearch` callback from `page.tsx` to trigger the results table
- All components are drop-in replacements for your existing files — same paths, same imports

