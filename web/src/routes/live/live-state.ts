export interface StaticParameters {
	time_per_step: number;
	dt: number;
	mu: number;
	sigma: number;
	T: number;
}

export interface DynamicParameters {
	tau: number;
}

export interface FinalParameters {
	var5: number;
	cvar5: number;
}

export interface Assets {
	underlying: number;
	option: number;
	cash: number;
}

export interface LiveData {
	time: number;
	gbm: number[];
	price: number[];
	delta: number[];
	assets: Assets;
}

export interface LiveState {
	playing: boolean;
	static_parameters: StaticParameters;
	dynamic_parameters: DynamicParameters;
	final_parameters: FinalParameters | null;
	live_data: (LiveData | null)[];
}
