import React from "react";
import { Train, Calendar, Users, Bookmark, FileText } from "lucide-react";

interface TicketCardProps {
  trainNumber: string;
  trainName?: string;
  source: string;
  destination: string;
  date: string;
  coachClass: string;
  quota: string;
  wlNumber: number;
}

export default function TicketCard({
  trainNumber,
  trainName = "Express",
  source,
  destination,
  date,
  coachClass,
  quota,
  wlNumber,
}: TicketCardProps) {
  // Format dates elegantly
  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }).toUpperCase();
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="relative w-full bg-[#2a2420] border-l-4 border-[#f5a623] rounded-r-xl border border-y-[#3d3530] border-r-[#3d3530] overflow-hidden shadow-2xl">
      {/* Background Watermark stamp (Physical ticket design) */}
      <div className="absolute right-10 bottom-2 text-[80px] font-mono font-bold text-[#231e1a] select-none pointer-events-none tracking-widest leading-none z-0 uppercase">
        IR-TKT
      </div>

      <div className="relative p-6 flex flex-col md:flex-row justify-between items-stretch gap-6 z-10">
        {/* Left main ticket pane */}
        <div className="flex-1 flex flex-col justify-between gap-4">
          {/* Header Metadata */}
          <div className="flex items-center justify-between border-b border-dashed border-[#3d3530] pb-3">
            <div className="flex items-center gap-2">
              <Train className="w-4 h-4 text-[#f5a623]" />
              <span className="font-mono text-xs font-bold text-[#e8e0d0]">
                TKT NO: {Math.floor(10000000 + Math.random() * 90000000)}
              </span>
            </div>
            <span className="font-mono text-xs font-bold text-[#a89880]">
              CLASS: {coachClass} | QUOTA: {quota}
            </span>
          </div>

          {/* Large Station Travel Hub */}
          <div className="flex items-center justify-between gap-4 my-2">
            <div className="text-left">
              <span className="block text-[10px] uppercase tracking-wider text-[#a89880]">DEPARTURE STATION</span>
              <span className="font-mono text-2xl md:text-3xl font-bold text-[#f5a623] tracking-wider amber-glow">
                {source}
              </span>
            </div>

            {/* Simulated route track */}
            <div className="flex-1 flex flex-col items-center">
              <span className="font-mono text-xs text-[#a89880] tracking-widest">{trainNumber}</span>
              <div className="relative w-full flex items-center justify-center my-1">
                <div className="w-full h-[2px] bg-[#3d3530] border-t border-dashed border-[#a89880]" />
                <div className="absolute w-2 h-2 rounded-full bg-[#f5a623] animate-pulse" />
              </div>
              <span className="text-[9px] text-[#5c5248] uppercase tracking-widest truncate max-w-[150px]">
                {trainName}
              </span>
            </div>

            <div className="text-right">
              <span className="block text-[10px] uppercase tracking-wider text-[#a89880]">ARRIVAL STATION</span>
              <span className="font-mono text-2xl md:text-3xl font-bold text-[#f5a623] tracking-wider amber-glow">
                {destination}
              </span>
            </div>
          </div>

          {/* Details Row */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-[#231f1a] p-3 rounded border border-[#3d3530]">
            <div>
              <span className="block text-[9px] uppercase tracking-wider text-[#5c5248]">JOURNEY DATE</span>
              <span className="font-mono text-xs text-[#e8e0d0] font-semibold">{formatDate(date)}</span>
            </div>
            <div>
              <span className="block text-[9px] uppercase tracking-wider text-[#5c5248]">WAITLIST NO</span>
              <span className="font-mono text-xs text-[#f5a623] font-bold">WL / {wlNumber}</span>
            </div>
            <div className="col-span-2 md:col-span-1">
              <span className="block text-[9px] uppercase tracking-wider text-[#5c5248]">PREDICTION STATUS</span>
              <span className="font-mono text-xs text-[#e8e0d0] font-semibold">ACTIVE INTEL</span>
            </div>
          </div>
        </div>

        {/* Perforated divider lines (Tear-off zone) */}
        <div className="hidden md:flex flex-col justify-between items-center px-2 relative">
          <div className="w-6 h-6 rounded-full bg-[#1a1612] absolute -top-9 border border-b-[#3d3530]" />
          <div className="h-full border-r-2 border-dashed border-[#3d3530]" />
          <div className="w-6 h-6 rounded-full bg-[#1a1612] absolute -bottom-9 border border-t-[#3d3530]" />
        </div>

        {/* Right stub (The Conductor Stub) */}
        <div className="w-full md:w-44 flex flex-col justify-between gap-4 border-t md:border-t-0 md:border-l border-dashed border-[#3d3530] pt-4 md:pt-0 md:pl-4">
          <div className="text-center md:text-left">
            <span className="block text-[9px] uppercase tracking-widest text-[#5c5248]">VERIFICATION STAMP</span>
            <div className="inline-block mt-1 px-2.5 py-1 border-2 border-[#f5a62320] text-[#f5a623] rounded text-[10px] font-mono tracking-wider font-semibold transform -rotate-1">
              BOARD OK
            </div>
          </div>

          {/* Barcode artwork */}
          <div className="flex flex-col items-center md:items-start gap-1">
            <div className="flex items-end gap-[1.5px] h-10 w-full opacity-60">
              {Array.from({ length: 28 }).map((_, i) => (
                <div
                  key={i}
                  className="bg-[#e8e0d0]"
                  style={{
                    width: i % 4 === 0 ? "3px" : i % 3 === 0 ? "1px" : "1.5px",
                    height: `${40 - (i % 5) * 4}px`,
                  }}
                />
              ))}
            </div>
            <span className="text-[9px] font-mono text-[#5c5248] tracking-widest select-none">
              *RAILHACK-{trainNumber}*
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
