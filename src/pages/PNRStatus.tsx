import { useState } from "react";
import { Search, Train, CheckCircle2, XCircle, AlertTriangle, RefreshCw, Hash } from "lucide-react";
import VerdictBadge from "../components/VerdictBadge";

interface Passenger {
  passenger_number: number;
  coach: string;
  berth: number | null;
  current_status: string;
  booking_status: string;
  confirmation_probability: number;
  verdict: string;
}

interface PNRData {
  pnr: string;
  train_number: string;
  train_name: string;
  source: string;
  destination: string;
  journey_date: string;
  coach_class: string;
  quota: string;
  distance_km: number;
  chart_status: string;
  passengers: Passenger[];
  overall_probability: number;
  verdict: string;
  confidence: string;
}

const SAMPLE_PNRS = ["4521309876", "2234567890", "8876543210", "6612309871"];

export default function PNRStatus() {
  const [pnr, setPnr]         = useState("");
  const [data, setData]       = useState<PNRData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const fetchPNR = async (pnrVal: string) => {
    const clean = pnrVal.trim();
    if (clean.length !== 10 || !/^\d+$/.test(clean)) {
      setError("PNR must be exactly 10 digits.");
      return;
    }
    setError("");
    setLoading(true);
    setData(null);
    try {
      const res = await fetch(`/api/pnr/${clean}`);
      if (!res.ok) {
        const e = await res.json();
        setError(e.detail || "Failed to fetch PNR.");
        return;
      }
      setData(await res.json());
    } catch {
      setError("Network error. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const statusColor = (status: string) => {
    if (status.startsWith("CNF")) return "text-[#27ae60]";
    if (status.startsWith("RAC")) return "text-[#f39c12]";
    return "text-[#c0392b]";
  };

  const statusIcon = (status: string) => {
    if (status.startsWith("CNF"))
      return <CheckCircle2 className="w-4 h-4 text-[#27ae60] shrink-0" />;
    if (status.startsWith("RAC"))
      return <AlertTriangle className="w-4 h-4 text-[#f39c12] shrink-0" />;
    return <XCircle className="w-4 h-4 text-[#c0392b] shrink-0" />;
  };

  const probBar = (prob: number) => {
    const color =
      prob >= 65 ? "#27ae60" : prob >= 40 ? "#f39c12" : "#c0392b";
    return (
      <div className="w-full h-1.5 bg-[#1a1612] rounded-full overflow-hidden mt-1">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${prob}%`, backgroundColor: color }}
        />
      </div>
    );
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3 border-b border-[#3d3530] pb-4">
        <Hash className="w-6 h-6 text-[#f5a623]" />
        <div>
          <h1 className="text-xl font-mono text-[#f5a623] uppercase tracking-wider font-bold amber-glow">
            PNR STATUS CHECKER
          </h1>
          <p className="text-xs text-[#a89880]">
            Enter your 10-digit PNR to check confirmation probability.
          </p>
        </div>
      </div>

      {/* Input */}
      <div className="bg-[#231f1a] border border-[#3d3530] rounded-xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a89880]" />
            <input
              type="text"
              maxLength={10}
              value={pnr}
              onChange={(e) => setPnr(e.target.value.replace(/\D/g, ""))}
              onKeyDown={(e) => e.key === "Enter" && fetchPNR(pnr)}
              placeholder="Enter 10-digit PNR"
              className="w-full bg-[#1a1612] text-[#f5a623] font-mono text-lg py-3 pl-10 pr-4 rounded-lg border border-[#3d3530] focus:border-[#f5a623] outline-none transition-colors placeholder-[#5c5248] tracking-widest"
            />
          </div>
          <button
            onClick={() => fetchPNR(pnr)}
            disabled={loading}
            className="px-6 py-3 bg-[#f5a623] hover:bg-[#e0951a] text-[#1a1612] font-mono font-bold rounded-lg border border-[#f5a623] transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {loading
              ? <RefreshCw className="w-4 h-4 animate-spin" />
              : <Search className="w-4 h-4" />}
            CHECK PNR
          </button>
        </div>

        {/* Sample PNRs */}
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-[9px] font-mono text-[#5c5248] uppercase">TRY SAMPLE:</span>
          {SAMPLE_PNRS.map((s) => (
            <button
              key={s}
              onClick={() => { setPnr(s); fetchPNR(s); }}
              className="px-2 py-0.5 rounded bg-[#1a1612] border border-[#3d3530] text-[10px] font-mono text-[#a89880] hover:text-[#f5a623] hover:border-[#f5a62340] transition-colors tracking-wider"
            >
              {s}
            </button>
          ))}
        </div>

        {error && (
          <div className="p-3 rounded border border-red-900/30 bg-red-950/20 text-[#c0392b] text-xs font-mono">
            ERROR: {error}
          </div>
        )}
      </div>

      {/* Loading */}
      {loading && (
        <div className="bg-[#231f1a] border border-[#3d3530] rounded-xl p-10 text-center space-y-3">
          <RefreshCw className="w-8 h-8 text-[#f5a623] animate-spin mx-auto" />
          <p className="text-xs font-mono text-[#a89880] uppercase tracking-widest animate-pulse">
            FETCHING PNR DETAILS...
          </p>
        </div>
      )}

      {/* Result */}
      {data && !loading && (
        <div className="space-y-4">

          {/* Train Info Card */}
          <div className="bg-[#151210] border-2 border-[#3d3530] rounded-xl p-6 relative border-glow">
            <div className="absolute top-3 right-3">
              <span className={`text-[10px] font-mono font-bold px-2 py-1 rounded border ${
                data.chart_status === "Chart Prepared"
                  ? "border-[#27ae60] text-[#27ae60] bg-[rgba(39,174,96,0.08)]"
                  : "border-[#f5a623] text-[#f5a623] bg-[rgba(245,166,35,0.08)]"
              }`}>
                {data.chart_status === "Chart Prepared" ? "● CHART PREPARED" : "○ CHART NOT PREPARED"}
              </span>
            </div>

            <div className="space-y-4">
              <div>
                <span className="text-[9px] font-mono text-[#5c5248] uppercase tracking-widest">PNR NUMBER</span>
                <p className="text-2xl font-mono font-bold text-[#f5a623] tracking-widest amber-glow">
                  {data.pnr}
                </p>
              </div>

              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-t border-dashed border-[#3d3530] pt-4">
                <div>
                  <span className="text-[9px] font-mono text-[#5c5248] uppercase">TRAIN</span>
                  <p className="font-mono text-sm font-bold text-[#e8e0d0]">
                    #{data.train_number} — {data.train_name}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-[9px] font-mono text-[#5c5248] uppercase">JOURNEY DATE</span>
                  <p className="font-mono text-sm font-bold text-[#e8e0d0]">{data.journey_date}</p>
                </div>
              </div>

              <div className="flex items-center justify-between gap-4">
                <div className="text-center bg-[#231f1a] px-4 py-2 rounded border border-[#3d3530]">
                  <span className="text-[9px] font-mono text-[#a89880] block">FROM</span>
                  <span className="text-2xl font-mono font-bold text-[#f5a623]">{data.source}</span>
                </div>
                <div className="flex-1 text-center">
                  <div className="w-full h-[1px] border-t border-dashed border-[#3d3530] relative">
                    <Train className="w-4 h-4 text-[#f5a623] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#151210]" />
                  </div>
                  <span className="text-[9px] font-mono text-[#5c5248]">{data.distance_km} KM</span>
                </div>
                <div className="text-center bg-[#231f1a] px-4 py-2 rounded border border-[#3d3530]">
                  <span className="text-[9px] font-mono text-[#a89880] block">TO</span>
                  <span className="text-2xl font-mono font-bold text-[#f5a623]">{data.destination}</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center font-mono text-xs">
                <div className="bg-[#1e1915] p-2 rounded border border-[#3d3530]">
                  <span className="text-[9px] text-[#5c5248] block">CLASS</span>
                  <span className="text-[#e8e0d0] font-bold">{data.coach_class}</span>
                </div>
                <div className="bg-[#1e1915] p-2 rounded border border-[#3d3530]">
                  <span className="text-[9px] text-[#5c5248] block">QUOTA</span>
                  <span className="text-[#e8e0d0] font-bold">{data.quota.split(" ")[0]}</span>
                </div>
                <div className="bg-[#1e1915] p-2 rounded border border-[#3d3530]">
                  <span className="text-[9px] text-[#5c5248] block">OVERALL</span>
                  <span className="text-[#f5a623] font-bold">{data.overall_probability}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Overall verdict */}
          <div className="flex items-center justify-center gap-4 bg-[#231f1a] border border-[#3d3530] rounded-xl p-4">
            <div className="text-center">
              <span className="text-[9px] font-mono text-[#5c5248] uppercase block mb-2">OVERALL CONFIRMATION OUTLOOK</span>
              <VerdictBadge verdict={data.verdict} />
              <p className="text-[10px] font-mono text-[#a89880] mt-2">
                {data.confidence.toUpperCase()} confidence · {data.overall_probability}% probability
              </p>
            </div>
          </div>

          {/* Passengers */}
          <div className="bg-[#231f1a] border border-[#3d3530] rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-[#3d3530] pb-3">
              <h3 className="text-xs font-mono font-bold text-[#f5a623] tracking-wider uppercase">
                PASSENGER STATUS
              </h3>
              <span className="text-[9px] font-mono text-[#5c5248]">{data.passengers.length} PASSENGER(S)</span>
            </div>

            <div className="space-y-3">
              {data.passengers.map((p) => (
                <div key={p.passenger_number}
                  className="bg-[#1a1612] border border-[#3d3530] rounded-lg p-4 space-y-3">

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {statusIcon(p.current_status)}
                      <span className="text-xs font-mono font-bold text-[#e8e0d0]">
                        PASSENGER {p.passenger_number}
                      </span>
                    </div>
                    <VerdictBadge verdict={p.verdict} />
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center font-mono text-[10px]">
                    <div>
                      <span className="text-[#5c5248] block uppercase">Booked As</span>
                      <span className="text-[#a89880] font-semibold">{p.booking_status}</span>
                    </div>
                    <div>
                      <span className="text-[#5c5248] block uppercase">Current Status</span>
                      <span className={`font-bold ${statusColor(p.current_status)}`}>
                        {p.current_status}
                      </span>
                    </div>
                    <div>
                      <span className="text-[#5c5248] block uppercase">Coach</span>
                      <span className="text-[#e8e0d0] font-semibold">{p.coach}</span>
                    </div>
                    <div>
                      <span className="text-[#5c5248] block uppercase">Confirm %</span>
                      <span className="text-[#f5a623] font-bold">{p.confirmation_probability}%</span>
                    </div>
                  </div>

                  {probBar(p.confirmation_probability)}
                </div>
              ))}
            </div>

            <p className="text-[10px] font-mono text-[#5c5248] text-center pt-2 border-t border-[#3d3530]">
              ⚡ Simulated status based on historical WL clearance patterns · Not official IRCTC data
            </p>
          </div>

        </div>
      )}
    </div>
  );
}
