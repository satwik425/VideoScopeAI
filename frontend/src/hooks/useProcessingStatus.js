import { useEffect, useState } from "react";
import { getStatus } from "../services/api";

export function useProcessingStatus(videoId) {
  const [state, setState] = useState({ status: "idle", stage: null, progress: 0, errorCode: null, visualStatus: "pending" });

  useEffect(() => {
    if (!videoId) {
      setState({ status: "idle", stage: null, progress: 0, errorCode: null, visualStatus: "pending" });
      return;
    }
    let stopped = false;
    let timer;
    async function poll() {
      try {
        const s = await getStatus(videoId);
        if (stopped) return;
        setState({ status: s.status, stage: s.stage, progress: s.progress, errorCode: s.error_code, visualStatus: s.visual_status });
        if (s.status === "failed") return;
        // Keep polling after "ready" until the visual index settles.
        if (s.status === "ready" && (s.visual_status === "ready" || s.visual_status === "failed")) return;
      } catch {
        // transient error: keep polling
      }
      timer = setTimeout(poll, 2500);
    }
    setState({ status: "queued", stage: null, progress: 0, errorCode: null, visualStatus: "pending" });
    poll();
    return () => { stopped = true; clearTimeout(timer); };
  }, [videoId]);

  return state;
}
