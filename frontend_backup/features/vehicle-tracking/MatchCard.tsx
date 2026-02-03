import { MatchResult } from "./types";
import { Progress } from "@/components/ui/progress";

interface Props {
  match: MatchResult;
  onSelect: () => void;
  selected: boolean;
}

export default function MatchCard({ match, onSelect, selected }: Props) {
  return (
    <div
      onClick={onSelect}
      className={`cursor-pointer rounded-lg border p-3 transition ${
        selected
          ? "border-slate-400 bg-slate-900"
          : "border-slate-800 bg-slate-950 hover:bg-slate-900"
      }`}
    >
      <div className="mb-2 flex justify-between text-xs text-slate-400">
        <span>{match.cameraId}</span>
        <span>{match.similarity}% similarity</span>
      </div>
      <Progress value={match.similarity} />
    </div>
  );
}
