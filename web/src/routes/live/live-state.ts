export interface GBMPath {
  time: number;
  data: number[];
}

export interface DeltaPath {
  time: number;
  data: number;
}

export interface LiveState {
  playing: false;
  tau: number | null;
  gbm_paths: GBMPath[];
  delta: DeltaPath[];
}
