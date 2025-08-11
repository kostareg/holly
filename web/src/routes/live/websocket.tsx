import { Link2, Link2Off, LoaderCircle, Pause, Play, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import type { LiveState } from "@/routes/live/live-state";

enum SocketState {
  Connected,
  Connecting,
  Closed,
}

export const Websocket = ({
  setState,
}: {
  setState: (state: LiveState) => void;
}) => {
  // todo: allow users to specify a custom address
  const [conn, setConn] = useState<WebSocket | null>(null);
  const [socketState, setSocketState] = useState<SocketState>(
    SocketState.Closed,
  );
  const [playing, setPlaying] = useState<boolean>(false);

  const reloadConnection = () => {
    conn?.close();
    const ws = new WebSocket("ws://localhost:65135");
    setConn(ws);
    setSocketState(SocketState.Connecting);

    ws.addEventListener("open", () => setSocketState(SocketState.Connected));
    ws.addEventListener("message", (m) => {
      const data = JSON.parse(m.data);
      setState(data);
      setPlaying(data.playing);
    });
    ws.addEventListener("close", () => setSocketState(SocketState.Closed));
  };

  // biome-ignore-start lint/correctness/useExhaustiveDependencies: unset or reset on each rerender
  useEffect(() => {
    reloadConnection();

    return () => conn?.close();
  }, []);
  // biome-ignore-end lint/correctness/useExhaustiveDependencies: unset or reset on each rerender

  return (
    <div className="w-full pl-4 my-4 flex flex-row gap-2 items-center">
      {socketState === SocketState.Connected && (
        <>
          <Link2 className="text-emerald-500" /> websocket connected
        </>
      )}
      {socketState === SocketState.Connecting && (
        <>
          <LoaderCircle className="text-gray-500 animate-spin" /> websocket
          connecting...{" "}
        </>
      )}
      {socketState === SocketState.Closed && (
        <>
          <Link2Off className="text-rose-500" /> websocket disconnected
        </>
      )}

      <Button variant="secondary" size="icon" onClick={reloadConnection}>
        <RefreshCw />
      </Button>

      {playing ? <Button
        variant="secondary"
        size="icon"
        onClick={() => conn?.send(JSON.stringify({ action: "pause" }))}
      >
        <Pause />
      </Button> : <Button
        variant="secondary"
        size="icon"
        onClick={() => conn?.send(JSON.stringify({ action: "play" }))}
      >
        <Play />
      </Button>}
    </div>
  );
};

export default Websocket;
