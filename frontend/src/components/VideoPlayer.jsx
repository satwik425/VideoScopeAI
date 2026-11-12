import { forwardRef, useImperativeHandle, useRef } from "react";

const VideoPlayer = forwardRef(function VideoPlayer({ src }, ref) {
  const el = useRef(null);
  useImperativeHandle(ref, () => ({
    seekTo(seconds) {
      if (!el.current) return;
      el.current.currentTime = seconds;
      el.current.play().catch(() => {});
      el.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    },
  }));
  return <video ref={el} src={src} controls className="aspect-video w-full rounded-xl bg-black" />;
});

export default VideoPlayer;
