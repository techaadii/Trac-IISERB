import { useState } from "react";
import { MatchResult } from "@/features/vehicle-tracking/types";

export function useSelectedMatch() {
  const [selected, setSelected] = useState<MatchResult | null>(null);

  return {
    selected,
    selectMatch: setSelected,
  };
}
