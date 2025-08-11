import { ChartContainer, type ChartConfig } from "@/components/ui/chart";
import { Line, LineChart } from "recharts";

const data = [{ name: 'Some content', uv: 400, pv: 2400, amt: 2400 }, { uv: 100 }, { uv: 200 }];

const config = {} satisfies ChartConfig;

function Live() {
  return <div className="grid grid-cols-4 gap-4">
    <ChartContainer config={config} className="size-full">
      <LineChart data={data}>
        <Line dataKey="uv" />
      </LineChart>
    </ChartContainer>
  </div>;
}

export default Live;
