import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";

export default function QueryPanel() {
  return (
    <Card className="col-span-3 bg-slate-900 border-slate-800">
      <CardContent className="p-4">
        <h2 className="mb-3 text-sm font-medium text-slate-300">
          Query Vehicle
        </h2>

        <div className="flex h-40 items-center justify-center rounded-lg border border-dashed border-slate-700 bg-slate-950">
          <Upload className="h-6 w-6 text-slate-500" />
        </div>

        <Button className="mt-4 w-full bg-slate-200 text-slate-900 hover:bg-white">
          Run Query
        </Button>
      </CardContent>
    </Card>
  );
}
