const QUESTIONS = [
  "Summarize the main points of this video.",
  "What topics does the speaker cover?",
  "What diagram or slide is shown in the video?",
  "Where does the speaker give an example?",
];

export default function SuggestedQuestions({ onPick, disabled }) {
  return (
    <div className="flex flex-wrap gap-2">
      {QUESTIONS.map((q) => (
        <button key={q} disabled={disabled} onClick={() => onPick(q)}
          className="rounded-full border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800 disabled:opacity-40">
          {q}
        </button>
      ))}
    </div>
  );
}
