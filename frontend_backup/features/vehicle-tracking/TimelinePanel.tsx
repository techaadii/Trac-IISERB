import { Card, CardContent } from "@/components/ui/card";

export default function TimelinePanel() {
  return (
    <Card className="col-span-12 bg-slate-900 border-slate-800">
      <CardContent className="p-4">
        <h2 className="mb-3 text-sm font-medium text-slate-300">
          Vehicle Timeline Trace
        </h2>

        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span>Cam 3 — 14:32</span>
          <span>→</span>
          <span>Cam 1 — 14:41</span>
          <span>→</span>
          <span>Cam 7 — 15:05</span>
        </div>
      </CardContent>
    </Card>
  );
}
