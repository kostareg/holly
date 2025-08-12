import { Moon, ShieldPlus, Sun } from "lucide-react";
import { useState } from "react";
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import type { LiveState } from "@/routes/live/live-state";
import Websocket from "@/routes/live/websocket";

const config = {
  uv: {
    label: "UV",
    icon: Sun,
    color: "var(--color-yellow-500)",
  },
  pv: {
    label: "PV",
    icon: Moon,
    color: "var(--color-red-500)",
  },
  amt: {
    label: "AMT",
    icon: ShieldPlus,
    color: "var(--color-blue-500)",
  },
} satisfies ChartConfig;

function Live() {
  const [state, setState] = useState<LiveState>({
    playing: false,
    gbm_paths: [],
  });

  // reshape: [{ time, p0, p1, ... }]
  const seriesCount = 15;
  const chartData = state.gbm_paths.map(({ time, data }) => {
    const row: Record<string, number> = { time };
    for (let i = 0; i < seriesCount; i++) row[`p${i}`] = data?.at(i) || 0;
    return row;
  });

  return (
    <>
      <Websocket setState={setState} />
      <div className="grid grid-cols-3 gap-4">
        <ChartContainer config={config} className="size-full">
          <LineChart accessibilityLayer data={chartData}>
            {[...new Array(15).keys()].map((_, i) => (
              <Line
                dataKey={`p${i}`}
                stroke="var(--color-pv)"
                name={`Simulation ${i}`}
                dot={false}
                isAnimationActive={false}
              />
            ))}
            <CartesianGrid />
            <XAxis dataKey="time" />
            <YAxis />
            <ChartTooltip content={<ChartTooltipContent />} />
          </LineChart>
        </ChartContainer>
        {[...Array(15).keys()].map((n) => (
          <ChartContainer key={n} config={config} className="size-full">
            <LineChart accessibilityLayer>
              <CartesianGrid />
              <XAxis />
            </LineChart>
          </ChartContainer>
        ))}
      </div>
    </>
  );
}

export default Live;
