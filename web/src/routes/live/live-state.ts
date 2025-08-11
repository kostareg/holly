export interface SomeData {
  name: string,
  uv: number,
  pv: number,
  amt: number,
}

export interface LiveState {
  playing: false;
  some_data: SomeData[];
}
