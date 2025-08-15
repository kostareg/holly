import { LoaderCircle } from "lucide-react";
import { useState } from "react";
import { Label, Line, LineChart, ReferenceLine, XAxis, YAxis } from "recharts";
import Websocket from "@/components/common/websocket";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import {
	type ChartConfig,
	ChartContainer,
	ChartTooltip,
	ChartTooltipContent,
} from "@/components/ui/chart";
import type { LiveData, LiveState } from "@/routes/live/live-state";

const asset_config = {
	"assets.underlying": {
		label: "Underlying",
		color: "var(--chart-1)",
	},
	"assets.option": {
		label: "Option",
		color: "var(--chart-2)",
	},
	"assets.cash": {
		label: "Average cash",
		color: "var(--chart-3)",
	},
} satisfies ChartConfig;
const gbm_config = {} satisfies ChartConfig;
const delta_config = {} satisfies ChartConfig;
const price_config = {} satisfies ChartConfig;

const defaultLiveData = {
	time: 0,
	gbm: [],
	price: [],
	delta: [],
	assets: {
		underlying: 0,
		option: 0,
		cash: 0,
	},
} satisfies LiveData;

function Live() {
	const [state, setState] = useState<LiveState | null>(null);

	// reshape: [{ time, p0, p1, ... }]
	const gbm_count = 15;
	const gbm_data = state?.live_data.map((item) => {
		const { time, gbm } = item ?? defaultLiveData;
		const row: Record<string, number | null> = { time };
		for (let i = 0; i < gbm_count; i++) row[`p${i}`] = gbm.at(i) || null;
		return row;
	});

	const price_count = 15;
	const price_data = state?.live_data.map((item) => {
		const { time, price } = item ?? defaultLiveData;
		const row: Record<string, number | null> = { time };
		for (let i = 0; i < price_count; i++) row[`p${i}`] = price.at(i) || null;
		return row;
	});

	const delta_count = 15;
	const delta_data = state?.live_data.map((item) => {
		const { time, delta } = item ?? defaultLiveData;
		const row: Record<string, number | null> = { time };
		for (let i = 0; i < delta_count; i++) row[`p${i}`] = delta.at(i) || null;
		return row;
	});

	return (
		<>
			<Websocket setState={setState} />
			<div className="grid grid-cols-3 gap-4 p-4">
				<Card className="col-span-2">
					<CardHeader>
						<CardTitle>Details</CardTitle>
						<CardDescription>
							General details about the simulation configuration.
						</CardDescription>
					</CardHeader>
					<CardContent className="grid grid-cols-2 gap-4">
						<div>
							Static parameters:
							<ul className="list-disc list-inside">
								<li>
									Time per step:{" "}
									{state?.static_parameters.time_per_step || "unknown"} seconds
								</li>
								<li>
									dt (step size):{" "}
									{state?.static_parameters.dt
										? `1/${Math.round(1 / state.static_parameters.dt)}`
										: "unknown"}{" "}
									years
								</li>
								<li>
									μ (drift rate, annualized):{" "}
									{state ? state.static_parameters.mu * 100 : "unknown "}%
								</li>
								<li>
									σ (stddev volatility, annualized):{" "}
									{state ? state.static_parameters.sigma * 100 : "unknown "}%
								</li>
								<li>
									T (initial time until maturity):{" "}
									{state?.static_parameters.T || "unknown"} years
								</li>
							</ul>
						</div>
						<div>
							Dynamic parameters:
							<ul className="list-inside list-disc">
								<li>
									t (current time): {state?.live_data.at(-1)?.time || "unknown"}{" "}
									steps
								</li>
								<li>
									τ (time until maturity):{" "}
									{state?.dynamic_parameters.tau.toFixed(2) || "unknown"} years
								</li>
							</ul>
						</div>
						<div>
							Final parameters:
							<ul className="list-inside list-disc">
								<li>
									Mean Profit & Loss: $
									{state?.final_parameters?.pnl.toFixed(2) ||
										(state?.playing ? (
											<LoaderCircle
												size={20}
												className="text-gray-500 animate-spin inline"
											/>
										) : (
											"unknown"
										))}
								</li>
								<li>
									Value at Risk 5%: $
									{state?.final_parameters?.var5.toFixed(2) ||
										(state?.playing ? (
											<LoaderCircle
												size={20}
												className="text-gray-500 animate-spin inline"
											/>
										) : (
											"unknown"
										))}
								</li>
								<li>
									Conditional Value at Risk 5%: $
									{state?.final_parameters?.cvar5.toFixed(2) ||
										(state?.playing ? (
											<LoaderCircle
												size={20}
												className="text-gray-500 animate-spin inline"
											/>
										) : (
											"unknown"
										))}
								</li>
							</ul>
						</div>
					</CardContent>
				</Card>
				<Card>
					<CardHeader>
						<CardTitle>Assets</CardTitle>
						<CardDescription>
							Description of all assets that we hold throughout the process.
						</CardDescription>
					</CardHeader>
					<CardContent>
						<ChartContainer config={asset_config}>
							<LineChart accessibilityLayer data={state?.live_data}>
								<Line
									dataKey="assets.underlying"
									dot={false}
									isAnimationActive={false}
									yAxisId="price"
									stroke="var(--chart-1)"
								/>
								<Line
									dataKey="assets.option"
									dot={false}
									isAnimationActive={false}
									yAxisId="options"
									stroke="var(--chart-2)"
								/>
								<Line
									dataKey="assets.cash"
									dot={false}
									isAnimationActive={false}
									yAxisId="price"
									stroke="var(--chart-3)"
								/>
								<XAxis domain={[0, 100]} dataKey="time" interval={9}>
									<Label
										value="Time (steps)"
										position="insideBottom"
										offset={0}
									/>
								</XAxis>
								<YAxis
									yAxisId="price"
									orientation="left"
									domain={([min, max]) => {
										if (min === Infinity && max === -Infinity) return [0, 19];
										return [Math.floor(min - 5), Math.ceil(max + 5)];
									}}
								>
									<Label angle={-90}>Price ($)</Label>
								</YAxis>
								<YAxis yAxisId="options" orientation="right" domain={[0, 2]}>
									<Label angle={-90}>Options (#)</Label>
								</YAxis>
								<ChartTooltip
									content={<ChartTooltipContent labelKey="Assets" />}
								/>
							</LineChart>
						</ChartContainer>
					</CardContent>
				</Card>
				<Card className="size-full">
					<CardHeader>
						<CardTitle>Geometric Brownian Motion Simulation</CardTitle>
						<CardDescription>
							Simulates geometric brownian motion (GBM) of underlying asset
							value, which is later used to calculate option price. Only first
							15 paths are displayed.
						</CardDescription>
					</CardHeader>
					<CardContent>
						<ChartContainer config={gbm_config}>
							<LineChart accessibilityLayer data={gbm_data}>
								{[...new Array(gbm_count).keys()].map((v, i) => (
									<Line
										key={v}
										dataKey={`p${i}`}
										name={`Simulation ${i}`}
										dot={false}
										isAnimationActive={false}
									/>
								))}
								<ReferenceLine y={100} />
								<XAxis domain={[0, 100]} dataKey="time" interval={9}>
									<Label
										value="Time (steps)"
										position="insideBottom"
										offset={0}
									/>
								</XAxis>
								<YAxis
									allowDecimals={false}
									domain={([min, max]) => {
										if (min === Infinity && max === -Infinity)
											return [100, 100];
										const maxDiff = Math.max(
											Math.abs(100 - min),
											Math.abs(100 - max),
										);
										return [
											Math.floor(100 - maxDiff),
											Math.ceil(100 + maxDiff),
										];
									}}
								>
									<Label
										value="Price ($)"
										position="insideLeft"
										angle={-90}
										offset={20}
									/>
								</YAxis>
								<ChartTooltip content={<ChartTooltipContent />} />
							</LineChart>
						</ChartContainer>
					</CardContent>
				</Card>
				<Card>
					<CardHeader>
						<CardTitle>Black-Scholes Price</CardTitle>
						<CardDescription>
							Describes the current fair price of an option of the underlying
							asset.
						</CardDescription>
					</CardHeader>
					<CardContent>
						<ChartContainer config={price_config}>
							<LineChart accessibilityLayer data={price_data}>
								{[...new Array(price_count).keys()].map((v, i) => (
									<Line
										key={v}
										dataKey={`p${i}`}
										dot={false}
										isAnimationActive={false}
										name={`Simulation ${i}`}
									/>
								))}
								<XAxis domain={[0, 100]} dataKey="time" interval={9}>
									<Label
										value="Time (steps)"
										position="insideBottom"
										offset={0}
									/>
								</XAxis>
								<YAxis
									allowDecimals={false}
									domain={([min, max]) => {
										if (min === Infinity && max === -Infinity) return [0, 19];
										return [0, Math.ceil(max + 5)];
									}}
								>
									<Label
										value="Price ($)"
										position="insideLeft"
										angle={-90}
										offset={20}
									/>
								</YAxis>
								<ChartTooltip content={<ChartTooltipContent />} />
							</LineChart>
						</ChartContainer>
					</CardContent>
				</Card>
				<Card className="size-full">
					<CardHeader>
						<CardTitle>Delta</CardTitle>
						<CardDescription>
							Describes the sensitivity of the option's price given a $1 change
							in the underlying price.
						</CardDescription>
					</CardHeader>
					<CardContent>
						<ChartContainer config={delta_config}>
							<LineChart accessibilityLayer data={delta_data}>
								{[...new Array(delta_count).keys()].map((v, i) => (
									<Line
										key={v}
										dataKey={`p${i}`}
										dot={false}
										isAnimationActive={false}
										name={`Simulation ${i}`}
									/>
								))}
								<XAxis domain={[0, 100]} dataKey="time" interval={9}>
									<Label
										value="Time (steps)"
										position="insideBottom"
										offset={0}
									/>
								</XAxis>
								<YAxis allowDecimals={false} domain={[0, 1]}>
									<Label
										value="Delta"
										position="insideLeft"
										angle={-90}
										offset={20}
									/>
								</YAxis>
								<ChartTooltip content={<ChartTooltipContent />} />
							</LineChart>
						</ChartContainer>
					</CardContent>
				</Card>
			</div>
		</>
	);
}

export default Live;
