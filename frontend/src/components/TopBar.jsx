export default function TopBar({ status, onReset, hasVideo }) {
  const label = { queued: "Queued", processing: "Processing", ready: "Ready", failed: "Failed" }[status];
  const color = { ready: "bg-emerald-400", failed: "bg-red-400" }[status] || "bg-amber-400 animate-pulse";
  return (
    <header className="flex items-center justify-between border-b border-slate-800 px-5 py-3">
      <span className="text-lg font-semibold tracking-tight">
        VidScope <span className="text-indigo-400">AI</span>
      </span>
      <div className="flex items-center gap-4">
        {label && (
          <span className="flex items-center gap-2 text-sm text-slate-300">
            <span className={`h-2 w-2 rounded-full ${color}`} /> {label}
          </span>
        )}
        {hasVideo && (
          <button onClick={onReset} className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm hover:bg-slate-800">
            New video
          </button>
        )}
      </div>
    </header>
  );
}
