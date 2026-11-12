import { formatTime } from "../utils/formatTime";

export default function TimestampChip({ seconds, onSeek }) {
  return (
    <button
      onClick={() => onSeek(seconds)}
      className="rounded-md bg-indigo-500/15 px-2 py-0.5 font-mono text-xs text-indigo-300 hover:bg-indigo-500/30"
    >
      {formatTime(seconds)}
    </button>
  );
}
