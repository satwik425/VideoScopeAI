const STAGES = {
  probing: "Inspecting video",
  extracting_audio: "Extracting audio",
  transcribing: "Transcribing speech",
  indexing: "Building search index",
};
const ERRORS = {
  ffmpeg_not_installed: "FFmpeg is not installed on the server.",
  invalid_media: "This file isn't a valid video.",
  no_audio_stream: "This video has no audio track.",
  audio_extraction_failed: "Could not extract audio from this video.",
  no_speech_detected: "No speech was detected in this video.",
};

export default function ProcessingStatus({ status, stage, progress, errorCode, visualStatus }) {
  if (status === "ready") {
    const visual = {
      ready: ["text-emerald-400", "Visual search ready."],
      failed: ["text-amber-400", "Visual search unavailable for this video (transcript Q&A still works)."],
    }[visualStatus] || ["text-slate-400", "Indexing video frames for visual search…"];
    return (
      <div className="space-y-1">
        <p className="text-sm text-emerald-400">Transcript ready. Ask away.</p>
        <p className={`text-xs ${visual[0]}`}>{visual[1]}</p>
      </div>
    );
  }
  if (status === "failed")
    return <p role="alert" className="text-sm text-red-400">{ERRORS[errorCode] || "Processing failed."}</p>;
  return (
    <div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div className="h-full bg-indigo-500 transition-all" style={{ width: `${progress}%` }} />
      </div>
      <p className="mt-2 text-sm text-slate-400">{STAGES[stage] || "Waiting to start"}…</p>
    </div>
  );
}
