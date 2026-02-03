"use client";

import { Card, CardContent } from "@/components/ui/card";
import { mockMatches } from "@/data/mockMatches";
import MatchCard from "./MatchCard";
import { useSelectedMatch } from "@/hooks/useSelectedMatch";

export default function MatchList() {
  const { selected, selectMatch } = useSelectedMatch();

  return (
    <Card className="col-span-5 bg-slate-900 border-slate-800">
      <CardContent className="p-4">
        <h2 className="mb-4 text-sm font-medium text-slate-300">
          Top Matches Across Cameras
        </h2>

        <div className="space-y-4">
          {mockMatches.map((match) => (
            <MatchCard
              key={match.id}
              match={match}
              selected={selected?.id === match.id}
              onSelect={() => selectMatch(match)}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
