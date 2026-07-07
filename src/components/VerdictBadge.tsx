interface VerdictBadgeProps {
  verdict: "likely" | "borderline" | "unlikely" | string;
}

export default function VerdictBadge({ verdict }: VerdictBadgeProps) {
  const normVerdict = verdict.toLowerCase().trim();

  let label = "BORDERLINE";
  let styles = "border-[#f39c12] text-[#f39c12] bg-[rgba(243,156,18,0.08)] shadow-[0_0_8px_rgba(243,156,18,0.15)]";

  if (normVerdict === "likely" || normVerdict === "confirm likely" || normVerdict === "confirm_likely") {
    label = "CONFIRM LIKELY";
    styles = "border-[#27ae60] text-[#27ae60] bg-[rgba(39,174,96,0.08)] shadow-[0_0_8px_rgba(39,174,96,0.15)]";
  } else if (normVerdict === "unlikely" || normVerdict === "unlikely confirm" || normVerdict === "unlikely_confirm") {
    label = "UNLIKELY";
    styles = "border-[#c0392b] text-[#c0392b] bg-[rgba(192,57,43,0.08)] shadow-[0_0_8px_rgba(192,57,43,0.15)]";
  }

  return (
    <div
      className={`inline-flex items-center px-4 py-1.5 rounded border text-xs font-mono font-bold tracking-wider uppercase select-none ${styles}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-2 animate-pulse" />
      {label}
    </div>
  );
}
