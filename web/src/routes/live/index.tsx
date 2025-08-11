import { Moon, ShieldPlus, Sun } from "lucide-react";
import { useState } from "react";
import { CartesianGrid, Line, LineChart, XAxis } from "recharts";
import {
  type ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
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
    some_data: [],
  });

  return (
    <>
      <Websocket setState={setState} />
      <div className="grid grid-cols-3 gap-4">
        <ChartContainer config={config} className="size-full">
          <LineChart accessibilityLayer data={state.some_data}>
            <Line
              dataKey="uv"
              stroke="var(--color-uv)"
              isAnimationActive={false}
            />
            <Line
              dataKey="pv"
              stroke="var(--color-pv)"
              isAnimationActive={false}
            />
            <Line
              dataKey="amt"
              stroke="var(--color-amt)"
              isAnimationActive={false}
            />
            <CartesianGrid />
            <XAxis dataKey="name" />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
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
