import { useState } from "react";
import { getConfig, uploadVideo } from "../services/api";

export function useVideoUpload() {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  async function upload(file) {
    setError(null);
    try {
      const cfg = await getConfig().catch(() => null);
      if (cfg) {
        if (file.size > cfg.max_upload_mb * 1024 * 1024) throw new Error(`File exceeds ${cfg.max_upload_mb} MB limit`);
        const ext = "." + file.name.split(".").pop().toLowerCase();
        if (!cfg.allowed_extensions.includes(ext)) throw new Error("Unsupported video format");
      }
      setUploading(true);
      setProgress(0);
      return await uploadVideo(file, setProgress);
    } catch (e) {
      setError(e.message);
      return null;
    } finally {
      setUploading(false);
    }
  }

  return { upload, progress, uploading, error, setError };
}
