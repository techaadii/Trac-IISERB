"use client";

import { Card, CardContent } from "@/components/ui/card";
import { useSelectedMatch } from "@/hooks/useSelectedMatch";

export default function ComparisonPanel() {
  const { selected } = useSelectedMatch();

  return (
    <Card className="col-span-4 bg-slate-900 border-slate-800">
      <CardContent className="p-4">
        <h2 className="mb-4 text-sm font-medium text-slate-300">
          Selected Comparison
        </h2>

        {selected ? (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="h-32 rounded-lg bg-slate-800" />
              <div className="h-32 rounded-lg bg-slate-800" />
            </div>

            <div className="mt-4 text-xs text-slate-400">
              Time Seen: {selected.timestamp}
              <br />
              Location: {selected.location}
            </div>
          </>
        ) : (
          <p className="text-xs text-slate-500">
            Select a match to compare vehicles.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
