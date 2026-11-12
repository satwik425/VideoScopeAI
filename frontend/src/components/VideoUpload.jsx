import { useRef, useState } from "react";

export default function VideoUpload({ onSelect, uploading, progress, error }) {
  const input = useRef(null);
  const [drag, setDrag] = useState(false);

  return (
    <div className="flex flex-1 items-center justify-center p-6">
      <div
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); const f = e.dataTransfer.files[0]; if (f) onSelect(f); }}
        className={`w-full max-w-xl rounded-2xl border-2 border-dashed p-12 text-center transition ${
          drag ? "border-indigo-400 bg-indigo-500/10" : "border-slate-700 bg-slate-900"
        }`}
      >
        <h1 className="text-2xl font-semibold">Upload a video. Ask questions.</h1>
        <p className="mt-2 text-sm text-slate-400">Jump to the exact moments that support the answer.</p>
        {uploading ? (
          <div className="mt-8">
            <div className="h-2 overflow-hidden rounded-full bg-slate-800">
              <div className="h-full bg-indigo-500 transition-all" style={{ width: `${progress}%` }} />
            </div>
            <p className="mt-2 text-sm text-slate-400">Uploading… {progress}%</p>
          </div>
        ) : (
          <>
            <button onClick={() => input.current.click()} className="mt-8 rounded-lg bg-indigo-500 px-5 py-2.5 font-medium hover:bg-indigo-400">
              Choose video
            </button>
            <p className="mt-3 text-xs text-slate-500">or drag and drop · MP4, MOV, MKV, WebM, AVI</p>
          </>
        )}
        {error && <p role="alert" className="mt-4 text-sm text-red-400">{error}</p>}
        <input ref={input} type="file" accept="video/*" hidden onChange={(e) => e.target.files[0] && onSelect(e.target.files[0])} />
      </div>
    </div>
  );
}
