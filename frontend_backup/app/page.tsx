import QueryPanel from "@/features/vehicle-tracking/QueryPanel";
import MatchList from "@/features/vehicle-tracking/MatchList";
import ComparisonPanel from "@/features/vehicle-tracking/ComparisonPanel";
import TimelinePanel from "@/features/vehicle-tracking/TimelinePanel";

export default function HomePage() {
  return (
    <div className="grid grid-cols-12 gap-6">
      <QueryPanel />
      <MatchList />
      <ComparisonPanel />
      <TimelinePanel />
    </div>
  );
}
