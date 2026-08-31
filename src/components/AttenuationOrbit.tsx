import type { AuditState } from "../types";
import PrecisionCheck from "./PrecisionCheck";

export default function AttenuationOrbit({ state, issueCount }: { state: AuditState; issueCount: number }) {
  return (
    <div className={`attenuation-orbit ${state}`} aria-hidden="true">
      <div className="orbit-halo" />
      <svg viewBox="0 0 180 180">
        <defs>
          <linearGradient id="orbit-gradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#55d5ef" />
            <stop offset="0.52" stopColor="#6a86ff" />
            <stop offset="1" stopColor="#a869ff" />
          </linearGradient>
          <filter id="soft-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2.2" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
        <circle className="orbit-ring ring-outer" cx="90" cy="90" r="72" />
        <circle className="orbit-ring ring-mid" cx="90" cy="90" r="52" />
        <circle className="orbit-ring ring-inner" cx="90" cy="90" r="32" />
        <path className="orbit-signal" d="M59 91h9l5-10 8 22 10-34 9 43 8-24 6 8h8" />
        <circle className="orbit-node node-a" cx="90" cy="18" r="2.5" />
        <circle className="orbit-node node-b" cx="142" cy="126" r="2.5" />
        <circle className="orbit-node node-c" cx="47" cy="53" r="2" />
      </svg>
      {state === "complete" && issueCount > 0 && <span className="orbit-count">{issueCount}</span>}
      {state === "complete" && issueCount === 0 && <span className="orbit-check"><PrecisionCheck size={16} /></span>}
    </div>
  );
}
