export interface StaticParameters {
  time_per_step: number;
  dt: number;
  mu: number;
  sigma: number;
  T: number;
}

export interface GBMPath {
  time: number;
  data: number[];
}

export interface DeltaPath {
  time: number;
  data: number;
}

export interface PricePath {
  time: number;
  data: number;
}

export interface LiveState {
  playing: false;
  static_parameters: StaticParameters | null;
  tau: number | null;
  gbm_paths: GBMPath[];
  delta: DeltaPath[];
  price: PricePath[];
}
