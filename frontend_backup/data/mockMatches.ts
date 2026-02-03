import { MatchResult } from "@/features/vehicle-tracking/types";

export const mockMatches: MatchResult[] = [
  {
    id: "1",
    cameraId: "Cam 3",
    similarity: 91,
    timestamp: "14:32",
    location: "Gate A",
  },
  {
    id: "2",
    cameraId: "Cam 7",
    similarity: 88,
    timestamp: "14:41",
    location: "Parking Lot",
  },
  {
    id: "3",
    cameraId: "Cam 1",
    similarity: 84,
    timestamp: "14:55",
    location: "Main Road",
  },
  {
    id: "4",
    cameraId: "Cam 9",
    similarity: 82,
    timestamp: "15:05",
    location: "Exit",
  },
];
