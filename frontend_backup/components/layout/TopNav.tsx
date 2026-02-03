export default function TopNav() {
  return (
    <header className="flex items-center justify-between border-b border-slate-800 px-6 py-3">
      <h1 className="text-lg font-semibold tracking-tight">
        Vehicle Tracking System
      </h1>
      <nav className="flex gap-6 text-sm text-slate-400">
        <span className="cursor-pointer hover:text-slate-200">Dataset</span>
        <span className="cursor-pointer hover:text-slate-200">Cameras</span>
        <span className="cursor-pointer hover:text-slate-200">Queries</span>
        <span className="cursor-pointer hover:text-slate-200">Timeline</span>
      </nav>
    </header>
  );
}
