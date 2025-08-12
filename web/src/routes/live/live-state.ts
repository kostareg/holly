export interface GBMPath {
  time: number;
  data: number[];
}

export interface LiveState {
  playing: false;
  gbm_paths: GBMPath[];
  tau: number | null;
}
