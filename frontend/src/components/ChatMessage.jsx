import { frameUrl } from "../services/api";
import TimestampChip from "./TimestampChip";

export default function ChatMessage({ message, videoId, onSeek }) {
  const user = message.role === "user";
  const frames = message.frames || [];
  return (
    <div className={`flex ${user ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
        user ? "bg-indigo-500 text-white" : message.status === "error" ? "bg-red-950 text-red-200" : "bg-slate-800 text-slate-100"
      }`}>
        <p className="whitespace-pre-wrap">{message.content}</p>
        {frames.length > 0 && (
          <div className="mt-3 border-t border-slate-700 pt-3">
            <p className="mb-2 text-xs uppercase tracking-wide text-slate-400">Visual evidence</p>
            <div className="grid grid-cols-2 gap-2">
              {frames.map((f) => (
                <div
                  key={f.frameId}
                  onClick={() => onSeek(f.timestamp)}
                  title="Jump to this moment"
                  className="group cursor-pointer overflow-hidden rounded-lg bg-slate-900 text-left ring-1 ring-slate-700 hover:ring-indigo-400"
                >
                  <img src={frameUrl(videoId, f.frameId)} alt={`Video frame at ${f.timestamp}s`} loading="lazy"
                    className="aspect-video w-full object-cover" />
                  <div className="flex items-center justify-between px-2 py-1.5">
                    <TimestampChip seconds={f.timestamp} onSeek={onSeek} />
                    <span className="text-[10px] text-slate-500">{f.match === "timestamp" ? "requested time" : "visual match"}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {message.evidence?.length > 0 && (
          <div className="mt-3 space-y-2 border-t border-slate-700 pt-3">
            <p className="text-xs uppercase tracking-wide text-slate-400">Transcript evidence</p>
            {message.evidence.map((e) => (
              <div key={e.chunkId} className="rounded-lg bg-slate-900 p-2.5">
                <TimestampChip seconds={e.start} onSeek={onSeek} />
                <p className="mt-1.5 line-clamp-3 text-xs text-slate-400">“{e.text}”</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
